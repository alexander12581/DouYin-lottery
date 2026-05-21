import logging
import time
from playwright.sync_api import sync_playwright, Request

from models import RequestContext

logger = logging.getLogger(__name__)

COMMENT_API_PATTERN = "/aweme/v1/web/comment/list/"
LOGIN_WAIT_TIMEOUT = 300  # 5 minutes for user to log in
INTERCEPT_TIMEOUT = 120  # 2 minutes to intercept a comment request after login


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
        self._browser_context = None

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

        # Extract cookies from the browser context (stored separately)
        cookies_list = self._browser_context.cookies()
        cookies = {c["name"]: c["value"] for c in cookies_list}

        aweme_id = extract_aweme_id_from_url(request.url)

        self._captured_context = RequestContext(
            headers=headers,
            cookies=cookies,
            aweme_id=aweme_id,
        )
        self._capture_done = True
        logger.info(f"Captured context for aweme_id={aweme_id}")

    def _wait_for_login(self, page):
        """Wait for user to log in. Returns True if login detected, False if timeout."""
        print("\n" + "=" * 50)
        print("  浏览器已打开，请在浏览器中登录抖音账号")
        print("  登录后工具会自动继续...")
        print("  (等待最多 5 分钟)")
        print("=" * 50 + "\n")

        deadline = time.time() + LOGIN_WAIT_TIMEOUT
        while time.time() < deadline:
            # Check if login elements are gone (logged in) or comment area is visible
            try:
                # If we can find comment-related elements, user is likely logged in
                has_login_popup = page.evaluate("""
                    () => {
                        const loginModal = document.querySelector('[class*="login"]') ||
                                          document.querySelector('[class*="Login"]');
                        return loginModal !== null;
                    }
                """)
                if not has_login_popup:
                    # No login popup visible, might be logged in
                    # Scroll down to trigger comments
                    page.evaluate("window.scrollTo(0, 300)")
                    page.wait_for_timeout(1000)

                    # Check again for comment request after scrolling
                    if self._capture_done:
                        return True
            except Exception:
                pass

            page.wait_for_timeout(2000)

        return self._capture_done

    def capture_request_context(self) -> RequestContext:
        """Open browser, wait for login, intercept comment request, return context."""
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
            context = browser.new_context()
            self._browser_context = context
            page = context.new_page()

            page.on("request", self._on_request)

            logger.info(f"Navigating to {self.video_url}")
            page.goto(self.video_url, wait_until="domcontentloaded")
            page.wait_for_timeout(3000)

            # Phase 1: Wait for user to log in
            self._wait_for_login(page)

            if not self._capture_done:
                # Phase 2: Login done or timeout, now actively try to intercept
                print("正在获取评论数据，请稍候...")
                deadline = time.time() + INTERCEPT_TIMEOUT
                while not self._capture_done and time.time() < deadline:
                    page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    page.wait_for_timeout(2000)

            browser.close()

            if self._captured_context is None:
                raise RuntimeError(
                    "未能拦截到评论API请求。请确保：\n"
                    "  1. 视频有评论\n"
                    "  2. 已登录抖音账号\n"
                    "  3. 视频页面加载完成"
                )

            return self._captured_context
