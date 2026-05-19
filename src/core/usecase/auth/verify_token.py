from src.core.entities.auth.session import UserSession
from src.core.contracts.auth.request.token_request import TokenRequest
from src.core.contracts.auth.request.cache_request import CacheRequest
from src.core.usecase.auth.errors import UnauthorizedError

class VerifyTokenUseCase:
    def __init__(self, token_request: TokenRequest, cache_request: CacheRequest):
        self._token_request = token_request
        self._cache_request = cache_request

    def execute(self, token: str) -> UserSession:
        # Decode and verify the JWT signature and basic expiration
        payload = self._token_request.decode(token)
        if not payload:
            raise UnauthorizedError("Invalid or expired token")

        # Extract user claims
        user_id = payload.get("id")
        username = payload.get("username")
        email = payload.get("email")

        if user_id is None or not username or not email:
            raise UnauthorizedError("Token payload is incomplete")

        # Retrieve the single active token from the cache
        active_token = self._cache_request.get_session(user_id)
        if not active_token:
            raise UnauthorizedError("No active session found for this user")

        # Check if this token matches the active one. If not, it means a new token "pisó" this one.
        if active_token != token:
            raise UnauthorizedError("Session has been invalidated by a newer login")

        # Return the verified domain session
        return UserSession(id=user_id, username=username, email=email)
