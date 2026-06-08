import bcrypt
import logging
import os
import smtplib
from datetime import datetime, timedelta, timezone
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from jose import jwt
<<<<<<< HEAD
from src.db.user import crear_usuario_db, email_existe, obtener_id_por_email, actualizar_alumno_db, crear_alumno_db
=======

from src.db.auth import obtener_usuario_por_email
from src.db.user import crear_usuario_db, email_existe
>>>>>>> c993e9837a372e3ef7a1798207ee12a6e43db778
from .constantes import MIN_CARACTERES_PASSWORD, TIEMPO_EXPIRACION_TOKEN_RESET_MINUTOS
from src.db.roles import ESTUDIANTE
from .errores import (
    PROHIBIDO_ESTUDIANTE,
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
    remitente = os.environ.get("EMAIL_SOPORTE")
    password_env = os.environ.get("EMAIL_PASSWORD")

    if remitente is None or password_env is None:
        return None, ERROR_ENVIO_MAIL

    usuario = obtener_usuario_por_email(destinatario)
    if usuario is None:
        return None, EMAIL_NO_EXISTE
    id_usuario = usuario["id"]

    token = crear_token_reset_password(id_usuario, destinatario)

    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Recuperación de contraseña - uniManage"
    mensaje.attach(MIMEText(f"Token para recuperar contraseña: {token}", "plain"))

    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password_env)
        servidor.sendmail(remitente, destinatario, mensaje.as_string())
        servidor.quit()
        return {"message": "Mail enviado"}, None
    except Exception as e:
        logging.error("Error al enviar el correo: %s", e)
        return None, ERROR_ENVIO_MAIL


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



def actualizar_alumno(user_id_target: int, datos: dict, requester_role_id: int) -> tuple:
    if requester_role_id == ESTUDIANTE:
        return None, PROHIBIDO_ESTUDIANTE
    datos_limpios = {
        "username": datos.get("username"),
        "email": datos.get("email"),
        "document": datos.get("document")
    }
    resultado = actualizar_alumno_db(user_id_target, datos_limpios)
    return resultado, None


def crear_alumno(datos: dict, requester_role_id: int) -> tuple:
    if requester_role_id == ESTUDIANTE:
        return None, PROHIBIDO_ESTUDIANTE
    resultado = crear_alumno_db(datos)
    return resultado, None