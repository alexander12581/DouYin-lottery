import logging
import time
from playwright.sync_api import sync_playwright, Request

from models import RequestContext

logger = logging.getLogger(__name__)

COMMENT_API_PATTERN = "/aweme/v1/web/comment/list/"
INTERCEPT_TIMEOUT = 60_000  # 1 minute to intercept a comment request


def extract_aweme_id_from_url(url: str) -> str:
    """Extract aweme_id from the intercepted request URL."""
    from urllib.parse import urlparse, parse_qs
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    return qs.get("aweme_id", [""])[0]


class BrowserManager:
    """Manages Playwright browser and intercepts Douyin comment API requests."""

    def __init__(self, video_url: str):
        self.video_url = video_url
        self._captured_context: RequestContext | None = None
        self._capture_done = False

    def _on_request(self, request: Request):
        """Callback for intercepted network requests."""
        if COMMENT_API_PATTERN not in request.url:
            return
        if self._capture_done:
            return

        logger.info("Intercepted comment/list request")

        headers = dict(request.headers)
        # Remove pseudo-headers that httpx doesn't need
        headers.pop(":method", None)
        headers.pop(":path", None)
        headers.pop(":authority", None)
        headers.pop(":scheme", None)

        # Extract cookies from the browser context
        cookies_list = request.context.cookies()
        cookies = {c["name"]: c["value"] for c in cookies_list}

        aweme_id = extract_aweme_id_from_url(request.url)

        self._captured_context = RequestContext(
            headers=headers,
            cookies=cookies,
            aweme_id=aweme_id,
        )
        self._capture_done = True
        logger.info(f"Captured context for aweme_id={aweme_id}")

    def capture_request_context(self) -> RequestContext:
        """Open browser, wait for login, intercept comment request, return context."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()

            page.on("request", self._on_request)

            logger.info(f"Navigating to {self.video_url}")
            page.goto(self.video_url, wait_until="domcontentloaded")

            logger.info("Waiting for comment API request... (scroll to load comments)")
            page.wait_for_timeout(3000)

            deadline = time.time() + INTERCEPT_TIMEOUT / 1000
            while not self._capture_done and time.time() < deadline:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)

            browser.close()

            if self._captured_context is None:
                raise RuntimeError(
                    "Failed to intercept comment API request. "
                    "Make sure the video has comments and you are logged in."
                )

            return self._captured_context
