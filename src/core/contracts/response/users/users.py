def create_user_reponse(user: dict) -> dict:
    return {
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"].isoformat(),
    }
