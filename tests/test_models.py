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
