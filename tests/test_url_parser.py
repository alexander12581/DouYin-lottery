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
