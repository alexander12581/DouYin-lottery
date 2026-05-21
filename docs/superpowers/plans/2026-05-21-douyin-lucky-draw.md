# 抖音评论区幸运用户抽取工具 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python CLI tool that uses Playwright to intercept Douyin's comment API signatures, fetches all comments via pagination, and randomly selects lucky users.

**Architecture:** Playwright opens a browser for user login, intercepts one comment/list request to extract headers and anti-bot signatures (a_bogus, msToken), then httpx reuses those signatures to paginate through all comments. Pure random selection picks N unique users.

**Tech Stack:** Python 3.10+, Playwright, httpx, pytest

---

## File Structure

```
D:/tiktok_project/
├── main.py              # CLI entry, flow orchestration
├── models.py            # CommentUser, RequestContext dataclasses
├── url_parser.py         # Extract aweme_id from Douyin URLs
├── api.py               # httpx client, pagination, comment fetching
├── browser.py           # Playwright browser, request interception
├── lottery.py           # Dedup + random selection
├── requirements.txt     # Dependencies
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_url_parser.py
│   ├── test_lottery.py
│   └── test_api.py
```

---

### Task 1: Project Setup

**Files:**
- Create: `requirements.txt`
- Create: `tests/__init__.py`

- [ ] **Step 1: Create requirements.txt**

```
playwright>=1.40.0
httpx>=0.25.0
pytest>=7.4.0
```

- [ ] **Step 2: Create tests/__init__.py**

```python
```

- [ ] **Step 3: Install dependencies**

Run: `cd D:/tiktok_project && pip install -r requirements.txt && playwright install chromium`

Expected: Dependencies installed, Chromium browser downloaded.

- [ ] **Step 4: Commit**

```bash
git add requirements.txt tests/__init__.py
git commit -m "chore: initialize project with dependencies"
```

---

### Task 2: Data Models

**Files:**
- Create: `models.py`
- Create: `tests/test_models.py`

- [ ] **Step 1: Write failing test for CommentUser**

```python
# tests/test_models.py
from models import CommentUser


def test_comment_user_creation():
    user = CommentUser(
        user_id="123",
        nickname="test_user",
        avatar_url="https://example.com/avatar.jpg",
        comment_text="恭喜！",
        comment_time=1779336420,
        homepage_url="https://www.douyin.com/user/123",
    )
    assert user.user_id == "123"
    assert user.nickname == "test_user"
    assert user.comment_text == "恭喜！"


def test_comment_user_homepage_link():
    user = CommentUser(
        user_id="456",
        nickname="user2",
        avatar_url="",
        comment_text="nice",
        comment_time=0,
        homepage_url="https://www.douyin.com/user/456",
    )
    assert "456" in user.homepage_url
```

- [ ] **Step 2: Run test to verify it fails**

Run: `cd D:/tiktok_project && python -m pytest tests/test_models.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'models'`

- [ ] **Step 3: Write CommentUser and RequestContext dataclasses**

```python
# models.py
from dataclasses import dataclass


@dataclass
class CommentUser:
    user_id: str
    nickname: str
    avatar_url: str
    comment_text: str
    comment_time: int
    homepage_url: str


@dataclass
class RequestContext:
    headers: dict
    cookies: dict
    aweme_id: str
```

- [ ] **Step 4: Run test to verify it passes**

Run: `cd D:/tiktok_project && python -m pytest tests/test_models.py -v`

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add models.py tests/test_models.py
git commit -m "feat: add CommentUser dataclass"
```

---

### Task 3: URL Parser

**Files:**
- Create: `url_parser.py`
- Create: `tests/test_url_parser.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_url_parser.py
import pytest
from url_parser import extract_aweme_id


def test_video_url():
    url = "https://www.douyin.com/video/7640797086758263921"
    assert extract_aweme_id(url) == "7640797086758263921"


def test_jingxuan_url():
    url = "https://www.douyin.com/jingxuan?modal_id=7640797086758263921"
    assert extract_aweme_id(url) == "7640797086758263921"


def test_url_with_extra_params():
    url = "https://www.douyin.com/video/7640797086758263921?from=share"
    assert extract_aweme_id(url) == "7640797086758263921"


def test_invalid_url():
    with pytest.raises(ValueError):
        extract_aweme_id("https://www.douyin.com/")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/tiktok_project && python -m pytest tests/test_url_parser.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'url_parser'`

- [ ] **Step 3: Write URL parser**

```python
# url_parser.py
import re
from urllib.parse import urlparse, parse_qs


def extract_aweme_id(url: str) -> str:
    """Extract aweme_id from a Douyin video URL.

    Supported formats:
    - https://www.douyin.com/video/<id>
    - https://www.douyin.com/jingxuan?modal_id=<id>
    """
    parsed = urlparse(url)

    # Format: /video/<id>
    match = re.search(r"/video/(\d+)", parsed.path)
    if match:
        return match.group(1)

    # Format: ?modal_id=<id>
    qs = parse_qs(parsed.query)
    if "modal_id" in qs:
        return qs["modal_id"][0]

    raise ValueError(f"Cannot extract aweme_id from URL: {url}")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/tiktok_project && python -m pytest tests/test_url_parser.py -v`

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add url_parser.py tests/test_url_parser.py
git commit -m "feat: add URL parser for extracting aweme_id"
```

---

### Task 4: Lottery Logic

**Files:**
- Create: `lottery.py`
- Create: `tests/test_lottery.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_lottery.py
import pytest
from models import CommentUser
from lottery import draw_lucky_users


def _make_user(user_id: str, nickname: str = "user") -> CommentUser:
    return CommentUser(
        user_id=user_id,
        nickname=nickname,
        avatar_url="",
        comment_text="test",
        comment_time=0,
        homepage_url=f"https://www.douyin.com/user/{user_id}",
    )


def test_draw_returns_correct_count():
    users = [_make_user(str(i)) for i in range(10)]
    winners = draw_lucky_users(users, count=3)
    assert len(winners) == 3


def test_draw_deduplicates_by_user_id():
    users = [
        _make_user("1", "alice"),
        _make_user("1", "alice_dup"),
        _make_user("2", "bob"),
        _make_user("3", "charlie"),
    ]
    winners = draw_lucky_users(users, count=2)
    winner_ids = {u.user_id for u in winners}
    assert len(winner_ids) == 2
    assert "1" in winner_ids  # only one entry for user 1


def test_draw_returns_all_when_count_exceeds_unique():
    users = [_make_user("1"), _make_user("2")]
    winners = draw_lucky_users(users, count=5)
    assert len(winners) == 2


def test_draw_raises_on_empty_list():
    with pytest.raises(ValueError):
        draw_lucky_users([], count=1)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/tiktok_project && python -m pytest tests/test_lottery.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'lottery'`

- [ ] **Step 3: Write lottery module**

```python
# lottery.py
import random
from models import CommentUser


def draw_lucky_users(users: list[CommentUser], count: int) -> list[CommentUser]:
    """Draw `count` lucky users from the list, deduplicating by user_id."""
    if not users:
        raise ValueError("User list is empty")

    # Deduplicate: keep first occurrence per user_id
    seen = set()
    unique_users = []
    for u in users:
        if u.user_id not in seen:
            seen.add(u.user_id)
            unique_users.append(u)

    count = min(count, len(unique_users))
    return random.sample(unique_users, count)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/tiktok_project && python -m pytest tests/test_lottery.py -v`

Expected: PASS (4 tests)

- [ ] **Step 5: Commit**

```bash
git add lottery.py tests/test_lottery.py
git commit -m "feat: add lottery logic with dedup and random selection"
```

---

### Task 5: API Client

**Files:**
- Create: `api.py`
- Create: `tests/test_api.py`

- [ ] **Step 1: Write failing tests for comment parsing**

```python
# tests/test_api.py
from api import parse_comment_response


SAMPLE_RESPONSE = {
    "comments": [
        {
            "cid": "c1",
            "text": "恭喜！",
            "create_time": 1779336420,
            "user": {
                "uid": "u1",
                "nickname": "alice",
                "avatar_thumb": {
                    "url_list": ["https://example.com/a.jpg"],
                },
                "sec_uid": "sec_u1",
            },
        },
        {
            "cid": "c2",
            "text": "太棒了",
            "create_time": 1779336500,
            "user": {
                "uid": "u2",
                "nickname": "bob",
                "avatar_thumb": {
                    "url_list": ["https://example.com/b.jpg"],
                },
                "sec_uid": "sec_u2",
            },
        },
    ],
    "cursor": 20,
    "has_more": 1,
    "total": 100,
}


def test_parse_comments():
    users, cursor, has_more = parse_comment_response(SAMPLE_RESPONSE)
    assert len(users) == 2
    assert users[0].user_id == "u1"
    assert users[0].nickname == "alice"
    assert users[0].comment_text == "恭喜！"
    assert users[1].user_id == "u2"
    assert cursor == 20
    assert has_more is True


def test_parse_empty_comments():
    users, cursor, has_more = parse_comment_response({"comments": [], "cursor": 0, "has_more": 0})
    assert len(users) == 0
    assert has_more is False
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd D:/tiktok_project && python -m pytest tests/test_api.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'api'`

- [ ] **Step 3: Write API client with parse function**

```python
# api.py
import time
import logging
from typing import Optional

import httpx

from models import CommentUser

logger = logging.getLogger(__name__)

COMMENT_LIST_URL = "https://www.douyin.com/aweme/v1/web/comment/list/"
DEFAULT_COUNT = 20
REQUEST_DELAY = 1.0  # seconds between requests


def parse_comment_response(data: dict) -> tuple[list[CommentUser], int, bool]:
    """Parse API response into CommentUser list, cursor, and has_more flag."""
    comments = data.get("comments", [])
    users = []
    for c in comments:
        user_info = c.get("user", {})
        avatar_urls = user_info.get("avatar_thumb", {}).get("url_list", [])
        sec_uid = user_info.get("sec_uid", "")
        users.append(
            CommentUser(
                user_id=user_info.get("uid", ""),
                nickname=user_info.get("nickname", ""),
                avatar_url=avatar_urls[0] if avatar_urls else "",
                comment_text=c.get("text", ""),
                comment_time=c.get("create_time", 0),
                homepage_url=f"https://www.douyin.com/user/{sec_uid}" if sec_uid else "",
            )
        )
    cursor = data.get("cursor", 0)
    has_more = bool(data.get("has_more", 0))
    return users, cursor, has_more


class DouyinCommentClient:
    """Fetches all comments for a Douyin video using intercepted signatures."""

    def __init__(self, headers: dict, cookies: dict, aweme_id: str):
        self.headers = headers
        self.cookies = cookies
        self.aweme_id = aweme_id
        self._client: Optional[httpx.Client] = None

    def _get_client(self) -> httpx.Client:
        if self._client is None or self._client.is_closed:
            self._client = httpx.Client(
                headers=self.headers,
                cookies=self.cookies,
                timeout=30.0,
                follow_redirects=True,
            )
        return self._client

    def fetch_page(self, cursor: int = 0, count: int = DEFAULT_COUNT) -> dict:
        """Fetch a single page of comments."""
        params = {
            "device_platform": "webapp",
            "aid": "6383",
            "channel": "channel_pc_web",
            "aweme_id": self.aweme_id,
            "cursor": str(cursor),
            "count": str(count),
            "item_type": "0",
        }
        client = self._get_client()
        resp = client.get(COMMENT_LIST_URL, params=params)
        resp.raise_for_status()
        return resp.json()

    def fetch_all_comments(self, count: int = DEFAULT_COUNT) -> list[CommentUser]:
        """Fetch all comments by paginating through the API."""
        all_users = []
        cursor = 0
        page = 0

        while True:
            page += 1
            logger.info(f"Fetching page {page}, cursor={cursor}")
            try:
                data = self.fetch_page(cursor=cursor, count=count)
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP error on page {page}: {e}")
                raise
            except httpx.RequestError as e:
                logger.error(f"Request error on page {page}: {e}")
                raise

            users, cursor, has_more = parse_comment_response(data)
            all_users.extend(users)
            logger.info(f"Got {len(users)} comments, total so far: {len(all_users)}")

            if not has_more:
                break

            time.sleep(REQUEST_DELAY)

        return all_users

    def close(self):
        if self._client and not self._client.is_closed:
            self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd D:/tiktok_project && python -m pytest tests/test_api.py -v`

Expected: PASS (2 tests)

- [ ] **Step 5: Commit**

```bash
git add api.py tests/test_api.py
git commit -m "feat: add API client with comment parsing and pagination"
```

---

### Task 6: Browser Automation

**Files:**
- Create: `browser.py`

- [ ] **Step 1: Write browser module**

```python
# browser.py
import logging
from playwright.sync_api import sync_playwright, Page, Request

from models import CommentUser, RequestContext

logger = logging.getLogger(__name__)

COMMENT_API_PATTERN = "/aweme/v1/web/comment/list/"
LOGIN_CHECK_TIMEOUT = 120_000  # 2 minutes for user to log in
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

            # Wait for the comment request to be intercepted
            logger.info("Waiting for comment API request... (scroll down to load comments)")
            try:
                page.wait_for_timeout(3000)  # initial wait for page load
                # Scroll to trigger comment loading
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_function(
                    "() => window.__commentCaptured === true" if False else "false",
                    timeout=INTERCEPT_TIMEOUT,
                )
            except Exception:
                # The wait_for_function will always timeout since we set it to "false"
                # We rely on the _on_request callback setting _capture_done
                pass

            # Check if we captured the context via polling
            import time
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
```

- [ ] **Step 2: Commit**

```bash
git add browser.py
git commit -m "feat: add Playwright browser automation for signature interception"
```

---

### Task 7: Main CLI Entry Point

**Files:**
- Create: `main.py`

- [ ] **Step 1: Write main.py**

```python
# main.py
import argparse
import logging
import sys

from url_parser import extract_aweme_id
from browser import BrowserManager
from api import DouyinCommentClient
from lottery import draw_lucky_users

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="抖音评论区幸运用户抽取工具")
    parser.add_argument("url", help="抖音视频URL")
    parser.add_argument("--count", type=int, default=5, help="抽取人数 (默认: 5)")
    args = parser.parse_args()

    # Validate URL
    try:
        aweme_id = extract_aweme_id(args.url)
        logger.info(f"Extracted aweme_id: {aweme_id}")
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Step 1: Open browser and intercept signatures
    logger.info("Opening browser... Please log in if needed.")
    browser = BrowserManager(args.url)
    try:
        ctx = browser.capture_request_context()
    except RuntimeError as e:
        logger.error(str(e))
        sys.exit(1)

    logger.info(f"Signature captured. Fetching comments for video {ctx.aweme_id}...")

    # Step 2: Fetch all comments
    try:
        with DouyinCommentClient(
            headers=ctx.headers,
            cookies=ctx.cookies,
            aweme_id=ctx.aweme_id,
        ) as client:
            all_comments = client.fetch_all_comments()
    except Exception as e:
        logger.error(f"Failed to fetch comments: {e}")
        sys.exit(1)

    logger.info(f"Total comments fetched: {len(all_comments)}")

    # Step 3: Draw lucky users
    if not all_comments:
        logger.error("No comments found.")
        sys.exit(1)

    try:
        winners = draw_lucky_users(all_comments, count=args.count)
    except ValueError as e:
        logger.error(str(e))
        sys.exit(1)

    # Step 4: Display results
    print("\n" + "=" * 50)
    print(f"  恭喜以下 {len(winners)} 位幸运用户！")
    print("=" * 50)
    for i, winner in enumerate(winners, 1):
        print(f"\n  [{i}] {winner.nickname}")
        print(f"      评论: {winner.comment_text}")
        print(f"      主页: {winner.homepage_url}")
    print("\n" + "=" * 50)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Commit**

```bash
git add main.py
git commit -m "feat: add CLI entry point with full workflow"
```

---

### Task 8: Integration Test

**Files:**
- Modify: `browser.py` (fix polling logic)

- [ ] **Step 1: Fix browser.py polling logic**

The current `capture_request_context` uses a `wait_for_function("false")` hack. Replace with proper polling:

```python
# browser.py - replace the capture_request_context method body after page.goto

    def capture_request_context(self) -> RequestContext:
        """Open browser, wait for login, intercept comment request, return context."""
        import time

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
```

- [ ] **Step 2: Run all tests**

Run: `cd D:/tiktok_project && python -m pytest tests/ -v`

Expected: All unit tests PASS (8 tests)

- [ ] **Step 3: Manual integration test**

Run: `cd D:/tiktok_project && python main.py "https://www.douyin.com/video/7640797086758263921" --count 3`

Expected: Browser opens → user logs in → comments fetched → 3 lucky users displayed

- [ ] **Step 4: Commit**

```bash
git add browser.py
git commit -m "fix: improve browser polling logic for comment interception"
```
