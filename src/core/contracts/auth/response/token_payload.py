from dataclasses import dataclass
from src.core.entities.auth.session import UserSession

@dataclass(frozen=True)
class TokenPayload:
    id: int
    username: str
    email: str

    @classmethod
    def from_session(cls, session: UserSession) -> "TokenPayload":
        return cls(
            id=session.id,
            username=session.username,
            email=session.email
        )

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email
        }
