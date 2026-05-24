import os
import uuid
from datetime import datetime, timedelta
from functools import wraps

from flask import g, jsonify, request
from jose import JWTError, jwt

from src.db import auth as db_auth
from .errores import TOKEN_INVALIDO

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "supersecretkey")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
TIEMPO_EXPIRACION = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


def _crear_jwt(usuario_id: int, username: str, email: str, expira_en: datetime) -> str:
    payload = {
        "sub": str(usuario_id),
        "username": username,
        "email": email,
        "exp": int(expira_en.timestamp()),
        "iat": int(datetime.now().timestamp()),
        "jti": str(uuid.uuid4()),
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
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization", "").removeprefix("Bearer ").strip()
        usuario, error = verificar_token(token)

        if error:
            return jsonify({"error": error["error"]}), error["status"]

        g.current_user = usuario
        return func(*args, **kwargs)

    return wrapper
