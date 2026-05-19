from abc import ABC, abstractmethod


class CacheResponse(ABC):
    @abstractmethod
    def save_session(self, user_id: int, token: str, ttl_seconds: int) -> None:
        pass

    @abstractmethod
    def delete_session(self, user_id: int) -> None:
        pass
