from typing import Any
from src.core.contracts.auth.request.token_request import TokenRequest


class GetTokenClaimUseCase:
    def __init__(self, token_request: TokenRequest):
        self._token_request = token_request

    def execute(self, token: str, claim: str) -> Any:
        return self._token_request.get_claim(token, claim)
