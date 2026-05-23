from flask import jsonify, request

from src.core.usecase.auth.errors import UnauthorizedError
from src.providers.auth.auth_providers import get_verify_token_usecase
from src.providers.classroom.classroom_providers import (
    get_list_classroom_teachers_usecase,
)


def _extract_token() -> str:
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


def list_classroom_professors(classroom_id: int):
    try:
        session = get_verify_token_usecase().execute(_extract_token())
    except UnauthorizedError as exc:
        return jsonify({"error": str(exc)}), 401

    professors, error = get_list_classroom_teachers_usecase().execute(
        classroom_id, session.id
    )

    if error:
        return jsonify(error), 403

    return jsonify(professors), 200
