from jose import jwt
from datetime import datetime, timedelta
from src.db.user import create_User_db, email_exists
from src.funciones.errores import (
    EMAIL_NO_EXISTE,
    EMAIL_NO_VALIDO,
    EMAIL_YA_EXISTE,
    CONTRASENA_DEBIL,
)
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

MIN_CARACTERES = 6

TOKEN_KEY = os.environ.get("TOKEN_KEY")
TOKEN_ALGORITHM = os.environ.get("TOKEN_ALGORITHM")


def create_token(user_id: int, email: str) -> str:
    expiracion = datetime.now(datetime.timezone.utc) + timedelta(minutes=15)

    payload = {
        "sub": str(user_id),
        "email": email,
        "exp": expiracion,
        "tipo": "reset_password",
    }

    token = jwt.encode(payload, TOKEN_KEY, algorithm=TOKEN_ALGORITHM)
    return token


def send_password_mail(destinatario, id_usuario):
    if not email_exists(destinatario):
        return EMAIL_NO_EXISTE
    # funcion para enviar mail con token
    remitente = os.environ.get("EMAIL_SOPORTE")
    password = os.environ.get("EMAIL_PASSWORD")
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Recuperación de contraseña - uniManage"

    cuerpo = f"""
    Enviar un token para recuperar contraseña. {create_token(id_usuario, destinatario)}
    
    """
    mensaje.attach(MIMEText(cuerpo, "plain"))
    try:
        servidor = smtplib.SMTP("smtp.gmail.com", 587)
        servidor.starttls()
        servidor.login(remitente, password)
        texto = mensaje.as_string()
        servidor.sendmail(remitente, destinatario, texto)
        servidor.quit()
        return True

    except Exception as e:
        print(f"Error al enviar el correo: {e}")
        return False


def create_user(user: dict) -> dict:
    if email_exists(user["email"]):
        return EMAIL_YA_EXISTE
    if "@" not in user["email"]:
        return EMAIL_NO_VALIDO
    if len(user["password"]) < MIN_CARACTERES:
        return CONTRASENA_DEBIL

    return create_User_db(user)
