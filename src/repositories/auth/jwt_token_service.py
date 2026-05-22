import os
import time
import uuid
from typing import Any, Optional, cast
from jose import jwt, JWTError
from src.core.contracts.auth.request.token_request import TokenRequest
from src.core.contracts.auth.response.token_response import TokenResponse


class JWTTokenService(TokenRequest, TokenResponse):
    def __init__(self, secret_key: Optional[str] = None, algorithm: str = "HS256"):

        if secret_key:
            self._secret_key = secret_key
        else:
            self._secret_key = cast(
                str,
                os.getenv(
                    "JWT_SECRET",
                    "default-system-gestion-educativa-jwt-secret-key-987654321",
                ),
            )
        self._algorithm = algorithm

    def encode(self, payload: dict) -> str:
        data = payload.copy()
        if "exp" not in data:
            data["exp"] = int(time.time() + 86400)
        if "jti" not in data:
            data["jti"] = str(uuid.uuid4())
        return jwt.encode(data, self._secret_key, algorithm=self._algorithm)

    def decode(self, token: str) -> Optional[dict]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError:
            return None

    def get_claim(self, token: str, claim: str) -> Any:
        try:
            claims = jwt.get_unverified_claims(token)
            return claims.get(claim)
        except JWTError:
            return None
