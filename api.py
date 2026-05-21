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
