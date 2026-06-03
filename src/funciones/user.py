from src.db.user import create_User_db, email_exists
from src.funciones.errores import (
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    CONTRASENA_DEBIL,
)


def create_user(user: dict) -> dict:
    if email_exists(user["email"]):
        return EMAIL_YA_EXISTE
    if "@" not in user["email"]:
        return EMAIL_NO_VALIDO
    if len(user["password"]) < 6:
        return CONTRASENA_DEBIL

    return create_User_db(user)
