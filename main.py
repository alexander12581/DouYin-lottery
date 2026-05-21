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
