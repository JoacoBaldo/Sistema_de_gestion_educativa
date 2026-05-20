from src.core.entities.users.users import User
import bcrypt
from src.repositories.users.create_user import create_UserRepository
from src.core.contracts.response.users.users import create_user_reponse

def hash_pasword(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def validate_user_data(user: dict) -> dict:
    if not user.get("username") or not user.get("email") or not user.get("password"):
        return {"error": "Username, email, and password are required", "status_code": 400}
    if len(user["password"]) < 6:
        return {"error": "Password must be at least 6 characters long", "status_code": 400}
    if "@" not in user["email"]:
        return {"error": "Invalid email format", "status_code": 400}
    return None

def execute(user_requests: User) -> dict:
    if validate_user_data(user_requests) != None:
        return validate_user_data(user_requests)
    
    hashed_password = hash_pasword(user_requests["password"])
    user_requests["password"] = hashed_password

    if create_UserRepository(user_requests):
        return create_UserRepository(user_requests)
    
    user_reponse = user_requests.copy()
    del user_reponse["password"]
    return create_user_reponse(user_reponse)
