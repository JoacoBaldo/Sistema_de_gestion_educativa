from src.core.entities.users.users import User


def create_user_request(user: User) -> dict:
    return {
        "username": user["username"],
        "email": user["email"],
        "password": user["password"],
    }
