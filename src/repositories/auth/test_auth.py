import time
from src.core.usecase.auth.errors import UnauthorizedError
from src.core.usecase.auth.password_service import PasswordService
from src.core.usecase.auth.create_token import CreateTokenUseCase
from src.core.usecase.auth.verify_token import VerifyTokenUseCase
from src.core.usecase.auth.get_token_claim import GetTokenClaimUseCase
from src.repositories.auth.in_memory_cache import InMemoryCache
from src.repositories.auth.jwt_token_service import JWTTokenService


def test_password_service():
    service = PasswordService()
    password = "MySecurePassword123"
    hashed = service.hash_password(password)
    assert hashed != password
    assert len(hashed) > 0

    assert service.verify_password(password, hashed) is True

    assert service.verify_password("wrong_password", hashed) is False


def test_jwt_token_service_encode_decode():
    service = JWTTokenService(secret_key="test-secret")
    payload = {"id": 10, "username": "jdoe", "email": "jdoe@university.edu"}

    token = service.encode(payload)
    assert len(token) > 0

    decoded = service.decode(token)
    assert decoded is not None
    assert decoded["id"] == 10
    assert decoded["username"] == "jdoe"
    assert decoded["email"] == "jdoe@university.edu"
    assert "exp" in decoded


def test_jwt_token_service_get_claim():
    service = JWTTokenService(secret_key="test-secret")
    payload = {"id": 10, "username": "jdoe", "email": "jdoe@university.edu"}

    token = service.encode(payload)

    assert service.get_claim(token, "id") == 10
    assert service.get_claim(token, "username") == "jdoe"
    assert service.get_claim(token, "email") == "jdoe@university.edu"
    assert service.get_claim(token, "non_existent") is None


def test_get_token_claim_usecase():
    token_service = JWTTokenService(secret_key="test-secret")
    usecase = GetTokenClaimUseCase(token_request=token_service)

    payload = {"id": 42, "username": "clark", "email": "clark@dailyplanet.com"}
    token = token_service.encode(payload)

    assert usecase.execute(token, "id") == 42
    assert usecase.execute(token, "username") == "clark"
    assert usecase.execute(token, "email") == "clark@dailyplanet.com"
    assert usecase.execute(token, "non_existent") is None


def test_create_and_verify_token_flow():
    cache = InMemoryCache()
    token_service = JWTTokenService(secret_key="test-secret")

    create_usecase = CreateTokenUseCase(
        token_response=token_service, cache_response=cache
    )
    verify_usecase = VerifyTokenUseCase(
        token_request=token_service, cache_request=cache
    )

    token = create_usecase.execute(
        user_id=10, username="jdoe", email="jdoe@university.edu"
    )
    assert len(token) > 0

    session = verify_usecase.execute(token)
    assert session.id == 10
    assert session.username == "jdoe"
    assert session.email == "jdoe@university.edu"


def test_token_overwriting_single_session_security():
    cache = InMemoryCache()
    token_service = JWTTokenService(secret_key="test-secret")

    create_usecase = CreateTokenUseCase(
        token_response=token_service, cache_response=cache
    )
    verify_usecase = VerifyTokenUseCase(
        token_request=token_service, cache_request=cache
    )

    token_a = create_usecase.execute(
        user_id=10, username="jdoe", email="jdoe@university.edu"
    )

    session_a = verify_usecase.execute(token_a)
    assert session_a.id == 10

    token_b = create_usecase.execute(
        user_id=10, username="jdoe", email="jdoe@university.edu"
    )

    session_b = verify_usecase.execute(token_b)
    assert session_b.id == 10

    raised = False
    try:
        verify_usecase.execute(token_a)
    except UnauthorizedError as e:
        raised = True
        assert "Session has been invalidated by a newer login" in str(e)
    assert raised, "Should have raised UnauthorizedError for overwritten token A"


def test_token_expiration_ttl():
    cache = InMemoryCache()
    token_service = JWTTokenService(secret_key="test-secret")

    create_usecase = CreateTokenUseCase(
        token_response=token_service, cache_response=cache
    )
    verify_usecase = VerifyTokenUseCase(
        token_request=token_service, cache_request=cache
    )

    token = create_usecase.execute(
        user_id=10, username="jdoe", email="jdoe@university.edu", ttl_seconds=1
    )

    assert verify_usecase.execute(token).id == 10

    time.sleep(1.2)

    raised = False
    try:
        verify_usecase.execute(token)
    except UnauthorizedError as e:
        raised = True
        assert "No active session found for this user" in str(e)
    assert raised, "Should have raised UnauthorizedError for expired TTL session"
