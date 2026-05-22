from __future__ import annotations

from typing import Dict, Optional, TypedDict


class ErrorInfo(TypedDict):
    message: str
    status_code: int
    code: str


class AppError(Exception):
    """Base application exception."""


class ValidationError(AppError):
    """Validation failed for request or domain data."""


class AuthenticationError(AppError):
    """Authentication or authorization failed."""


class ConflictError(AppError):
    """Resource conflict or uniqueness violation."""


class DatabaseError(AppError):
    """Database access error."""


class InternalServerError(AppError):
    """Unexpected internal error."""


INVALID_JSON_BODY = "INVALID_JSON_BODY"
MISSING_REQUIRED_FIELDS = "MISSING_REQUIRED_FIELDS"
PASSWORD_TOO_SHORT = "PASSWORD_TOO_SHORT"
INVALID_EMAIL_FORMAT = "INVALID_EMAIL_FORMAT"
INVALID_EMAIL_DOMAIN = "INVALID_EMAIL_DOMAIN"
USER_EMAIL_ALREADY_EXISTS = "USER_EMAIL_ALREADY_EXISTS"
DATABASE_INTEGRITY_ERROR = "DATABASE_INTEGRITY_ERROR"
UNABLE_TO_CREATE_USER = "UNABLE_TO_CREATE_USER"
INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
INVALID_OR_EXPIRED_TOKEN = "INVALID_OR_EXPIRED_TOKEN"
TOKEN_PAYLOAD_INCOMPLETE = "TOKEN_PAYLOAD_INCOMPLETE"
NO_ACTIVE_SESSION = "NO_ACTIVE_SESSION"
SESSION_INVALIDATED = "SESSION_INVALIDATED"
INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
DATABASE_CONNECTION_ERROR = "DATABASE_CONNECTION_ERROR"

ERRORS: Dict[str, ErrorInfo] = {
    INVALID_JSON_BODY: {
        "code": INVALID_JSON_BODY,
        "message": "Invalid JSON body",
        "status_code": 400,
    },
    MISSING_REQUIRED_FIELDS: {
        "code": MISSING_REQUIRED_FIELDS,
        "message": "Username, email, and password are required",
        "status_code": 400,
    },
    PASSWORD_TOO_SHORT: {
        "code": PASSWORD_TOO_SHORT,
        "message": "Password must be at least 6 characters long",
        "status_code": 400,
    },
    INVALID_EMAIL_FORMAT: {
        "code": INVALID_EMAIL_FORMAT,
        "message": "Invalid email format",
        "status_code": 400,
    },
    INVALID_EMAIL_DOMAIN: {
        "code": INVALID_EMAIL_DOMAIN,
        "message": "Email must end with @fi.uba.ar",
        "status_code": 400,
    },
    USER_EMAIL_ALREADY_EXISTS: {
        "code": USER_EMAIL_ALREADY_EXISTS,
        "message": "User with this email already exists",
        "status_code": 409,
    },
    DATABASE_INTEGRITY_ERROR: {
        "code": DATABASE_INTEGRITY_ERROR,
        "message": "Database integrity error",
        "status_code": 500,
    },
    UNABLE_TO_CREATE_USER: {
        "code": UNABLE_TO_CREATE_USER,
        "message": "Unable to create user",
        "status_code": 500,
    },
    INTERNAL_SERVER_ERROR: {
        "code": INTERNAL_SERVER_ERROR,
        "message": "Internal server error",
        "status_code": 500,
    },
    INVALID_OR_EXPIRED_TOKEN: {
        "code": INVALID_OR_EXPIRED_TOKEN,
        "message": "Invalid or expired token",
        "status_code": 401,
    },
    TOKEN_PAYLOAD_INCOMPLETE: {
        "code": TOKEN_PAYLOAD_INCOMPLETE,
        "message": "Token payload is incomplete",
        "status_code": 401,
    },
    NO_ACTIVE_SESSION: {
        "code": NO_ACTIVE_SESSION,
        "message": "No active session found for this user",
        "status_code": 401,
    },
    SESSION_INVALIDATED: {
        "code": SESSION_INVALIDATED,
        "message": "Session has been invalidated by a newer login",
        "status_code": 401,
    },
    INVALID_CREDENTIALS: {
        "code": INVALID_CREDENTIALS,
        "message": "Invalid credentials",
        "status_code": 401,
    },
    DATABASE_CONNECTION_ERROR: {
        "code": DATABASE_CONNECTION_ERROR,
        "message": "Database connection error",
        "status_code": 500,
    },
}


def format_error_response(code: str, message: Optional[str] = None) -> dict:
    error_info = ERRORS.get(code)
    if error_info is None:
        return {"error": "Unknown error", "status_code": 500}
    return {
        "error": message or error_info["message"],
        "status_code": error_info["status_code"],
    }


def get_error_info(code: str) -> ErrorInfo:
    return ERRORS.get(
        code,
        {
            "code": "UNKNOWN_ERROR",
            "message": "Unknown error",
            "status_code": 500,
        },
    )
