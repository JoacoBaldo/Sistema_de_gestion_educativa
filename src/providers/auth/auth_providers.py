from src.core.usecase.auth.password_service import PasswordService
from src.core.usecase.auth.create_token import CreateTokenUseCase
from src.core.usecase.auth.verify_token import VerifyTokenUseCase
from src.core.usecase.auth.get_token_claim import GetTokenClaimUseCase
from src.repositories.auth.in_memory_cache import InMemoryCache
from src.repositories.auth.jwt_token_service import JWTTokenService

# Singleton instances of infrastructure and common services
_cache_instance = InMemoryCache()
_token_service_instance = JWTTokenService()
_password_service_instance = PasswordService()

def get_cache_repository() -> InMemoryCache:
    return _cache_instance

def get_token_service() -> JWTTokenService:
    return _token_service_instance

def get_password_service() -> PasswordService:
    return _password_service_instance

def get_create_token_usecase() -> CreateTokenUseCase:
    return CreateTokenUseCase(token_response=_token_service_instance, cache_response=_cache_instance)

def get_verify_token_usecase() -> VerifyTokenUseCase:
    return VerifyTokenUseCase(token_request=_token_service_instance, cache_request=_cache_instance)

def get_token_claim_usecase() -> GetTokenClaimUseCase:
    return GetTokenClaimUseCase(token_request=_token_service_instance)
