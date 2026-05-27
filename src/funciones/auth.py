import bcrypt
import os
from datetime import datetime, timedelta

from jose import JWTError, jwt

from src.db import auth as db_auth
from .errores import TOKEN_INVALIDO


JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")


def _validar_password(password: str, password_hash: str | bytes) -> bool:
    if isinstance(password_hash, str):
        password_hash = password_hash.encode("utf-8")

    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)
    except ValueError:
        return password == password_hash.decode("utf-8", errors="ignore")


TIEMPO_EXPIRACION = 24  # horas


def _crear_jwt(usuario_id: int, username: str, email: str, expira_en: datetime) -> str:
    payload = {
        "id": usuario_id,
        "username": username,
        "email": email,
        "exp": int(expira_en.timestamp()),
        "iat": int(datetime.now().timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verificar_token(token: str) -> tuple:
    if not token:
        return None, TOKEN_INVALIDO

    try:
        jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None, TOKEN_INVALIDO

    usuario = db_auth.sesion_existe(token)
    if not usuario:
        return None, TOKEN_INVALIDO

    return usuario, None


def crear_token(usuario_id: int, username: str, email: str) -> str:
    db_auth.eliminar_sesiones_usuario(usuario_id)
    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION)
    token = _crear_jwt(usuario_id, username, email, expira_en)
    db_auth.guardar_sesion(usuario_id, token, expira_en)
    return token


def token_required(func):
    return func
