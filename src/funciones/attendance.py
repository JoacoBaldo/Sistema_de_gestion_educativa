from src.db import attendance as db_attendance
from src.db import classroom as db_classroom

from .errores import SIN_ACCESO
from datetime import datetime
from src.db.asistencia_db import (
    crear_evento_asistencia,
    inasistencia_db,
    obtener_estudiantes_classroom,
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


def sumar_inasistencia(classroom_id: int, fecha: datetime | None = None):
    if fecha is None:
        fecha = datetime.now()
    if not existe_classroom(classroom_id):
        return {"error": "El aula no existe"}, 404
    nuevo_evento_id = crear_evento_asistencia(
        classroom_id, "QR_CODE_PLACEHOLDER", fecha
    )
    estudiantes_id = obtener_estudiantes_classroom(classroom_id)
    for student_id in estudiantes_id:
        inasistencia_db(student_id, nuevo_evento_id, fecha)