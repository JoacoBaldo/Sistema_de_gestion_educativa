from src.db.user import create_User_db, email_exists
from src.funciones.errores import (
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    ERROR_ENVIO_MAIL,
)


def create_user(user: dict) -> dict:
    if email_exists(user["email"]):
        return EMAIL_YA_EXISTE
    if "@" not in user["email"]:
        return EMAIL_NO_VALIDO
    if len(user["password"]) < 6:
        return CONTRASENA_DEBIL

def create_user(user: dict) -> tuple:
    if email_existe(user["email"]):
        return None, EMAIL_YA_EXISTE
    if not user["email"].endswith("@fi.uba.ar"):
        return None, EMAIL_NO_VALIDO
    if len(user["password"]) < MIN_CARACTERES_PASSWORD:
        return None, CONTRASENA_DEBIL
    resultado = crear_usuario_db(user)
    return resultado, None
