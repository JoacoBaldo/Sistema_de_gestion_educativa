from dataclasses import dataclass


@dataclass(frozen=True)
class UserSession:
    id: int
    username: str
    email: str
