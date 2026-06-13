import base64
import io
import os

import qrcode
import requests

from src.db import attendance as db_attendance
from src.db import classroom as db_classroom

from .errores import (
    CLASSROOM_NO_EXISTE,
    CODIGO_INVALIDO,
    CODIGO_NO_CORRESPONDE,
    ERROR_ENVIO_MAIL,
    SIN_ACCESO,
    SIN_ESTUDIANTES,
)
from datetime import datetime
from src.db.attendance import (
    crear_codigos_por_alumno,
    crear_evento_asistencia,
    inasistencia_db,
    obtener_estudiantes_classroom,
    obtener_estudiantes_classroom_con_email,
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
    qr_b64 = base64.b64encode(buffer.getvalue()).decode()

    api_key = os.environ.get("SMTP_PASSWORD")
    remitente = os.environ.get("EMAIL_REMITENTE")

    payload = {
        "sender": {"name": "uniManage Soporte", "email": remitente},
        "to": [{"email": destinatario}],
        "subject": "Código de asistencia - uniManage",
        "textContent": (
            f"Hola,\n\nAdjuntamos tu código QR personal de asistencia.\n"
            f"También podés acceder directamente desde este enlace:\n{link}\n\n"
            f"Código: {code}"
        ),
        "attachment": [{"name": "qr_asistencia.png", "content": qr_b64}],
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "api-key": api_key,
    }

    try:
        response = requests.post(
            "https://api.brevo.com/v3/smtp/email", json=payload, headers=headers
        )
        if response.status_code == 201:
            return {"message": "Correo enviado"}, None
        return None, ERROR_ENVIO_MAIL
    except Exception:
        return None, ERROR_ENVIO_MAIL


def enviar_qr_a_estudiantes(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    estudiantes = obtener_estudiantes_classroom_con_email(classroom_id)
    if not estudiantes:
        return None, SIN_ESTUDIANTES

    fecha = datetime.now()
    evento_id = crear_evento_asistencia(classroom_id, "MULTI_QR", fecha)

    student_ids = [e["user_id"] for e in estudiantes]
    for student_id in student_ids:
        inasistencia_db(student_id, evento_id, fecha, delta=1)

    codigos = crear_codigos_por_alumno(evento_id, student_ids)

    enviados = 0
    fallidos = []
    for estudiante in estudiantes:
        _, error = _enviar_mail_qr(
            estudiante["email"], classroom_id, codigos[estudiante["user_id"]]
        )
        if error:
            fallidos.append(estudiante["email"])
        else:
            enviados += 1

    return {"enviados": enviados, "fallidos": fallidos}, None


def validar_asistencia(classroom_id: int, code: str, usuario_id: int) -> tuple:
    evento = obtener_evento_por_codigo(classroom_id, code)
    if not evento:
        return None, CODIGO_INVALIDO

    if evento["user_id"] != usuario_id:
        return None, CODIGO_NO_CORRESPONDE

    inasistencia_db(
        student_id=usuario_id,
        attendance_event_id=evento["id"],
        fecha=datetime.now(),
        delta=-1,
    )
    return {"mensaje": "Asistencia registrada con éxito"}, None