from src.db.user import create_User_db, email_exists, change_password_db
from src.funciones.errores import (
    EMAIL_NO_EXISTE,
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    CONTRASENA_DEBIL,
)


def change_password_mail(email: str) -> dict:
    if not email_exists(email):
        return EMAIL_NO_EXISTE
    # funcion para enviar mail con link para cambiar contraseña

    return {
        "message": "Enviamos el mail con las instrucciones para cambiar la contraseña.",
        "status_code": 200,
    }


def change_password(new_password_data: dict) -> dict:
    if not email_exists(new_password_data["email"]):
        return EMAIL_NO_EXISTE
    return change_password_db(new_password_data)


def create_user(user: dict) -> dict:
    if email_exists(user["email"]):
        return EMAIL_YA_EXISTE
    if "@fi.uba.ar" not in user["email"]:
        return EMAIL_NO_VALIDO
    if len(user["password"]) < 6:
        return CONTRASENA_DEBIL

    return create_User_db(user)
