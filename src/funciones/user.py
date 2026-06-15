import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage

import bcrypt
from jose import jwt, JWTError

from src.db.auth import obtener_usuario_por_email
from src.db.user import actualizar_password_db, crear_usuario_db, email_existe
from .constantes import MIN_CARACTERES_PASSWORD, TIEMPO_EXPIRACION_TOKEN_RESET_MINUTOS
from .errores import (
    CONTRASENA_DEBIL,
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    TOKEN_RESET_INVALIDO,
    TOKEN_RESET_TIPO_INVALIDO,
    USUARIO_NO_ENCONTRADO,
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

    host = os.environ.get("MAILTRAP_HOST")
    port = int(os.environ.get("MAILTRAP_PORT", "2525"))
    user = os.environ.get("MAILTRAP_USER")
    password = os.environ.get("MAILTRAP_PASSWORD")
    remitente = os.environ.get("EMAIL_REMITENTE")

    msg = EmailMessage()
    msg["Subject"] = "Recuperación de contraseña - uniManage"
    msg["From"] = f"uniManage Soporte <{remitente}>"
    msg["To"] = destinatario
    msg.set_content(
        "Hola,\n\n"
        "Recibimos una solicitud para restablecer la contraseña de tu cuenta.\n"
        f"Token de validación: {token}\n"
    )

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return {"message": "Correo enviado"}, None
    except Exception as e:
        return None, {"error": "La conexión falló", "status": 500}


def restablecer_password(token: str, nueva_password: str) -> tuple:
    if len(nueva_password) < MIN_CARACTERES_PASSWORD:
        return None, CONTRASENA_DEBIL

    try:
        payload = jwt.decode(token, TOKEN_KEY, algorithms=[TOKEN_ALGORITHM])
    except JWTError:
        return None, TOKEN_RESET_INVALIDO

    if payload.get("tipo") != "reset_password":
        return None, TOKEN_RESET_TIPO_INVALIDO

    user_id = int(payload["sub"])
    password_hash = bcrypt.hashpw(
        nueva_password.encode("utf-8"), bcrypt.gensalt()
    ).decode("utf-8")
    resultado = actualizar_password_db(user_id, password_hash)
    return resultado, None


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
