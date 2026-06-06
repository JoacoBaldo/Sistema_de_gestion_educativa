from datetime import datetime
from src.db.classroom import existe_classroom
from src.db.asistencia_db import (
    crear_evento_asistencia,
    obtener_estudiantes_classroom,
    inasistencia_db,
)


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
