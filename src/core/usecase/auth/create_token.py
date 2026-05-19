from src.core.entities.auth.session import UserSession
from src.core.contracts.auth.response.token_response import TokenResponse
from src.core.contracts.auth.response.cache_response import CacheResponse
from src.core.contracts.auth.response.token_payload import TokenPayload

class CreateTokenUseCase:
    def __init__(self, token_response: TokenResponse, cache_response: CacheResponse):
        self._token_response = token_response
        self._cache_response = cache_response

    def execute(self, user_id: int, username: str, email: str, ttl_seconds: int = 86400) -> str:
        # Create user session entity
        session = UserSession(id=user_id, username=username, email=email)
        
        # Build token payload utilizing the specific contract in the response subfolder
        payload = TokenPayload.from_session(session).to_dict()
        
        # Encode session details into a JWT token
        token = self._token_response.encode(payload)
        
        # Save token to CacheResponse interface. Indexing by user_id ensures the old token is overwritten (pisado).
        self._cache_response.save_session(user_id=session.id, token=token, ttl_seconds=ttl_seconds)
        
        return token
