from abc import ABC, abstractmethod
from typing import Optional

class CacheRequest(ABC):
    @abstractmethod
    def get_session(self, user_id: int) -> Optional[str]:
        pass
