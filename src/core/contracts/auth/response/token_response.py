from abc import ABC, abstractmethod


class TokenResponse(ABC):
    @abstractmethod
    def encode(self, payload: dict) -> str:
        pass
