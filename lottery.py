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
