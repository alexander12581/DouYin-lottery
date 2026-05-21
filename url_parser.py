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
