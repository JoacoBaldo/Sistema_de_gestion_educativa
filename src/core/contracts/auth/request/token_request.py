from abc import ABC, abstractmethod
from typing import Any, Optional

class TokenRequest(ABC):
    @abstractmethod
    def decode(self, token: str) -> Optional[dict]:
        pass

    @abstractmethod
    def get_claim(self, token: str, claim: str) -> Any:
        pass
