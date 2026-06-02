from datetime import datetime, timedelta

import bcrypt

from src.db import auth as db_auth
from .constantes import TIEMPO_EXPIRACION_HORAS
from .errores import CREDENCIALES_INVALIDAS, TOKEN_INVALIDO


def verificar_token(token: str) -> tuple:
    usuario = db_auth.sesion_existe(token)
    if not usuario:
        return None, TOKEN_INVALIDO
    return usuario, None


def crear_token(usuario_id: int, username: str, email: str) -> str:
    db_auth.eliminar_sesiones_usuario(usuario_id)
    token = db_auth.generar_token()
    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION_HORAS)
    db_auth.guardar_sesion(usuario_id, token, expira_en)
    return token


def validar_credenciales(email: str, password: str) -> tuple:
    usuario = db_auth.obtener_usuario_por_email(email)
    if not usuario:
        return None, CREDENCIALES_INVALIDAS

    if not bcrypt.checkpw(
        password.encode("utf-8"), usuario["password"].encode("utf-8")
    ):
        return None, CREDENCIALES_INVALIDAS

    return {
        "id": usuario["id"],
        "username": usuario["username"],
        "email": usuario["email"],
        "role_id": usuario["role_id"],
    }, None
