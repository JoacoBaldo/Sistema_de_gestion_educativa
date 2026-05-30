from src.db.user import create_User_db, email_exists, change_password_db
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


def change_password_mail(destinatario, link_recuperacion):
    if not email_exists(destinatario):
        return EMAIL_NO_EXISTE
    # funcion para enviar mail con link para cambiar contraseña
    remitente = os.environ.get("EMAIL_SOPORTE")
    password = os.environ.get("EMAIL_PASSWORD")
    mensaje = MIMEMultipart()
    mensaje["From"] = remitente
    mensaje["To"] = destinatario
    mensaje["Subject"] = "Recuperación de contraseña - uniManage"

    cuerpo = """
    Enviar un token para recuperar contraselña.
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
