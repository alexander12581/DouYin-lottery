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
