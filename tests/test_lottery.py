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
    assert "1" in winner_ids


def test_draw_returns_all_when_count_exceeds_unique():
    users = [_make_user("1"), _make_user("2")]
    winners = draw_lucky_users(users, count=5)
    assert len(winners) == 2


def test_draw_raises_on_empty_list():
    with pytest.raises(ValueError):
        draw_lucky_users([], count=1)
