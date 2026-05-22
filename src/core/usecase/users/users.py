import bcrypt
from typing import Optional

from src.core.entities.users.users import User
from src.error import (
    format_error_response,
    INVALID_EMAIL_DOMAIN,
    INVALID_EMAIL_FORMAT,
    MISSING_REQUIRED_FIELDS,
    PASSWORD_TOO_SHORT,
    USER_EMAIL_ALREADY_EXISTS,
)
from src.repositories.users.create_user import create_UserRepository, email_exists


def hash_pasword(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def validate_user_data(user: User) -> Optional[dict]:
    if not user.get("username") or not user.get("email") or not user.get("password"):
        return format_error_response(MISSING_REQUIRED_FIELDS)
    if len(user["password"]) < 6:
        return format_error_response(PASSWORD_TOO_SHORT)
    if "@" not in user["email"]:
        return format_error_response(INVALID_EMAIL_FORMAT)
    if not user["email"].endswith("@fi.uba.ar"):
        return format_error_response(INVALID_EMAIL_DOMAIN)
    return None


def execute(user_requests: User) -> dict:
    validation_result = validate_user_data(user_requests)
    if validation_result is not None:
        return validation_result

    # Check uniqueness of email in the database
    if email_exists(user_requests["email"]):
        return format_error_response(USER_EMAIL_ALREADY_EXISTS)

    hashed_password = hash_pasword(user_requests["password"])
    user_requests["password"] = hashed_password

    return create_UserRepository(user_requests)
