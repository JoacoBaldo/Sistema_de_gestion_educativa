from datetime import datetime, timedelta
from src.db import auth as db_auth
from .errores import TOKEN_INVALIDO


def verificar_token(token: str) -> tuple:
    usuario = db_auth.sesion_existe(token)
    if not usuario:
        return None, TOKEN_INVALIDO
    return usuario, None


def crear_token(usuario_id: int, username: str, email: str) -> str:
    token = db_auth.generar_token()
    expira_en = datetime.now() + timedelta(hours=24)
    db_auth.guardar_sesion(usuario_id, token, expira_en)
    return token
