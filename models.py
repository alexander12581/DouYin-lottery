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
