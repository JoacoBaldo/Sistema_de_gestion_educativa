from src.db import attendance as db_attendance
from src.db import classroom as db_classroom
from .errores import SIN_ACCESO


def obtener_inasistencias_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    total_eventos = db_attendance.contar_eventos_classroom(classroom_id)
    alumnos = db_attendance.obtener_inasistencias_por_alumno(classroom_id)

    if total_eventos == 0 or not alumnos:
        porcentaje_asistencia = 100.0
        inasistencias_promedio = 0.0
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
