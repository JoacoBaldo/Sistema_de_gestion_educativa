import io
import os
import smtplib
from email.message import EmailMessage

import qrcode

from src.db import attendance as db_attendance
from src.db import classroom as db_classroom

from .errores import (
    CLASSROOM_NO_EXISTE,
    CODIGO_INVALIDO,
    ERROR_ENVIO_MAIL,
    SIN_ACCESO,
    SIN_ESTUDIANTES,
)
from datetime import datetime
from src.db.attendance import (
    crear_evento_asistencia,
    inasistencia_db,
    obtener_estudiantes_classroom,
    obtener_evento_por_codigo,
)
from src.db.classroom import existe_classroom


FULL_ASISTENCIA = 100
FULL_INASISTENCIA = 0


def obtener_inasistencias_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    total_eventos = db_attendance.contar_eventos_classroom(classroom_id)
    alumnos = db_attendance.obtener_inasistencias_por_alumno(classroom_id)

    if total_eventos == 0 or not alumnos:
        porcentaje_asistencia: float = FULL_ASISTENCIA
        inasistencias_promedio: float = FULL_INASISTENCIA
    else:
        inasistencias_promedio = sum(a["inasistencias"] for a in alumnos) / len(alumnos)
        porcentaje_asistencia = round(
            100 * (total_eventos - inasistencias_promedio) / total_eventos, 2
        )

    return {
        "classroom_id": classroom_id,
        "total_events": total_eventos,
        "average_absences": round(inasistencias_promedio, 2),
        "attendance_percentage": porcentaje_asistencia,
        "students": alumnos,
    }, None


def sumar_inasistencia(
    classroom_id: int,
    fecha: datetime | None = None,
    delta: int = 1,
    usuario_id: int | None = None,
) -> tuple:
    if fecha is None:
        fecha = datetime.now()

    if not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if usuario_id and not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    nuevo_evento_id = crear_evento_asistencia(classroom_id, "QR_CODE_PLACEHOLDER", fecha)
    for student_id in obtener_estudiantes_classroom(classroom_id):
        inasistencia_db(student_id, nuevo_evento_id, fecha, delta=delta)

    return {"mensaje": "Inasistencia actualizada correctamente"}, None


def _enviar_mail_qr(destinatario: str, classroom_id: int, code: str) -> tuple:
    base_url = os.environ.get("BASE_URL", "http://127.0.0.1:5001")
    link = f"{base_url}/aulas/{classroom_id}/asistencia/validar?code={code}"

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    host = os.environ.get("MAILTRAP_HOST")
    port = int(os.environ.get("MAILTRAP_PORT", "2525"))
    user = os.environ.get("MAILTRAP_USER")
    password = os.environ.get("MAILTRAP_PASSWORD")
    remitente = os.environ.get("EMAIL_REMITENTE")

    msg = EmailMessage()
    msg["Subject"] = "Código de asistencia - uniManage"
    msg["From"] = f"uniManage Soporte <{remitente}>"
    msg["To"] = destinatario
    msg.set_content(
        f"Hola,\n\nAdjuntamos el código QR de asistencia de hoy.\n"
        f"También podés acceder directamente desde este enlace:\n{link}\n\n"
        f"Código: {code}"
    )
    msg.add_attachment(
        buffer.getvalue(),
        maintype="image",
        subtype="png",
        filename="qr_asistencia.png",
    )

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return {"message": "Correo enviado"}, None
    except Exception as e:
        return None, ERROR_ENVIO_MAIL


def enviar_qr_a_estudiantes(classroom_id: int, usuario_id: int, code: str) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    estudiantes = db_attendance.obtener_inasistencias_por_alumno(classroom_id)
    if not estudiantes:
        return None, SIN_ESTUDIANTES

    enviados = 0
    fallidos = []
    for estudiante in estudiantes:
        _, error = _enviar_mail_qr(estudiante["email"], classroom_id, code)
        if error:
            fallidos.append(estudiante["email"])
        else:
            enviados += 1

    return {"enviados": enviados, "fallidos": fallidos}, None


def validar_asistencia(classroom_id: int, code: str, usuario_id: int) -> tuple:
    evento = obtener_evento_por_codigo(classroom_id, code)
    if not evento:
        return None, CODIGO_INVALIDO

    inasistencia_db(
        student_id=usuario_id,
        attendance_event_id=evento["id"],
        fecha=datetime.now(),
        delta=-1,
    )
    return {"mensaje": "Asistencia registrada con éxito"}, None
