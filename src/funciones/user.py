import os
from datetime import datetime, timedelta, timezone
import requests

import bcrypt
from jose import jwt

from src.db.auth import obtener_usuario_por_email
from src.db.user import crear_usuario_db, email_existe
from .errores import USUARIO_NO_ENCONTRADO
from .constantes import MIN_CARACTERES_PASSWORD, TIEMPO_EXPIRACION_TOKEN_RESET_MINUTOS
from .errores import (
    CONTRASENA_DEBIL,
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
)

TOKEN_KEY = os.environ.get("TOKEN_KEY")
TOKEN_ALGORITHM = os.environ.get("TOKEN_ALGORITHM")


def crear_token_reset_password(user_id: int, email: str) -> str:
    if TOKEN_KEY is None or TOKEN_ALGORITHM is None:
        raise RuntimeError(
            "TOKEN_KEY and TOKEN_ALGORITHM environment variables must be set"
        )
    expiracion = datetime.now(timezone.utc) + timedelta(
        minutes=TIEMPO_EXPIRACION_TOKEN_RESET_MINUTOS
    )
    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expiracion,
        "tipo": "reset_password",
    }
    return jwt.encode(payload, TOKEN_KEY, algorithm=TOKEN_ALGORITHM)


def send_password_mail(destinatario: str) -> tuple:
    usuario = obtener_usuario_por_email(destinatario)
    if not usuario:
        return None, USUARIO_NO_ENCONTRADO
    
    user_id = usuario.get("id")
    email = usuario.get("email")
    
    if not user_id or not email:
        return None, USUARIO_NO_ENCONTRADO
    
    token = crear_token_reset_password(int(user_id), str(email))
    api_key = os.environ.get("BREVO_API_PASSWORD")
    remitente = os.environ.get("EMAIL_REMITENTE")

    url = "https://api.brevo.com/v3/smtp/email"

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key,
    }

    cuerpo_mail = f"""
    Hola,
    Recibimos una solicitud para restablecer la contraseña de tu cuenta. Este mail contiene
    un token de validación.  {token}
    """
    payload = {
        "sender": {"name": "uniManage Soporte", "email": remitente},
        "to": [{"email": destinatario}],
        "subject": "Recuperación de contraseña - uniManage",
        "textContent": cuerpo_mail,
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 201:
            return {"message": "Correo enviado"}, None
        else:
            return None, {"error": "No se acepto la solicitud.", "status": 401}

    except Exception:
        error = {"error": "La conexión fallo", "status": 500}
        return None, error


def create_user(user: dict) -> tuple:
    if email_existe(user["email"]):
        return None, EMAIL_YA_EXISTE
    if "@" not in user["email"]:
        return None, EMAIL_NO_VALIDO
    if len(user["password"]) < MIN_CARACTERES_PASSWORD:
        return None, CONTRASENA_DEBIL
    password_hasheada = bcrypt.hashpw(
        user["password"].encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    resultado = crear_usuario_db({**user, "password": password_hasheada})
    return resultado, None
