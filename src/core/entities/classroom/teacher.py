from datetime import datetime
from typing import NotRequired, TypedDict


class Teacher(TypedDict):
    username: str
    email: str
    id: NotRequired[int]
    joined_at: NotRequired[datetime]
