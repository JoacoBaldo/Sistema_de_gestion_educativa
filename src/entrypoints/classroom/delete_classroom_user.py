from flask import jsonify, request

from src.core.usecase.auth.errors import UnauthorizedError
from src.providers.auth.auth_providers import get_verify_token_usecase
from src.providers.classroom.classroom_providers import (
    get_delete_classroom_user_usecase,
)


def _extract_token() -> str:
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


def delete_classroom_user(classroom_id: int, user_id: int):
    try:
        session = get_verify_token_usecase().execute(_extract_token())
    except UnauthorizedError as exc:
        return jsonify({"error": str(exc)}), 401

    result, error = get_delete_classroom_user_usecase().execute(
        classroom_id, user_id, session.id
    )

    if error:
        return jsonify(error), 403

    return jsonify(result), 200
