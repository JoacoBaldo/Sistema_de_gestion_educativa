import bcrypt
from typing import Optional

from src.core.contracts.response.users.users import create_user_reponse
from src.core.entities.users.users import User
from src.repositories.users.create_user import create_UserRepository, email_exists


def hash_pasword(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed_password.decode("utf-8")


def validate_user_data(user: User) -> Optional[dict]:
    if not user.get("username") or not user.get("email") or not user.get("password"):
        return {
            "error": "Username, email, and password are required",
            "status_code": 400,
        }
    if len(user["password"]) < 6:
        return {
            "error": "Password must be at least 6 characters long",
            "status_code": 400,
        }
    if "@" not in user["email"]:
        return {"error": "Invalid email format", "status_code": 400}
    if not user["email"].endswith("@fi.uba.ar"):
        return {"error": "Email must end with @fi.uba.ar", "status_code": 400}
    return None


def execute(user_requests: User) -> dict:
    validation_result = validate_user_data(user_requests)
    if validation_result is not None:
        return validation_result

    # Check uniqueness of email in the database
    if email_exists(user_requests["email"]):
        return {"error": "User with this email already exists", "status_code": 409}

    hashed_password = hash_pasword(user_requests["password"])
    user_requests["password"] = hashed_password

    return create_UserRepository(user_requests)
