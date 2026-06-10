import logging
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
from jose import jwt

from src.db.auth import obtener_usuario_por_email
from src.db.user import crear_usuario_db, email_existe

from .constantes import MIN_CARACTERES_PASSWORD, TIEMPO_EXPIRACION_TOKEN_RESET_MINUTOS
from .errores import (
    CONTRASENA_DEBIL,
    EMAIL_NO_EXISTE,
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    ERROR_ENVIO_MAIL,
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
    servidor_smtp = os.environ.get("SMTP_SERVER")
    puerto_smtp = int(os.environ.get("SMTP_PORT", 587))
    usuario_smtp = os.environ.get("SMTP_USER")
    password_smtp = os.environ.get("SMTP_PASSWORD")
    remitente = os.environ.get("EMAIL_REMITENTE")

    if remitente is None or password_smtp is None:
        return None, ERROR_ENVIO_MAIL

    usuario = obtener_usuario_por_email(destinatario)
    if usuario is None:
        return None, EMAIL_NO_EXISTE
    id_usuario = usuario["id"]

    token = crear_token_reset_password(id_usuario, destinatario)

    mensaje = MIMEMultipart()
    mensaje["From"] = f"uniManage Soporte <{remitente}>"
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Recuperación de contraseña - uniManage"
    mensaje.attach(MIMEText(f"Token para recuperar contraseña: {token}", "plain"))

    try:
        servidor = smtplib.SMTP(servidor_smtp, puerto_smtp)
        servidor.starttls()
        servidor.login(usuario_smtp, password_smtp)
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        return True, None

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False, ERROR_ENVIO_MAIL


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
