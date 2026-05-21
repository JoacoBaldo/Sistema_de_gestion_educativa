from datetime import datetime
from typing import NotRequired, TypedDict


class User(TypedDict):
    username: str
    email: str
    password: str
    id: NotRequired[int]
    created_at: NotRequired[datetime]
