from src.db import attendance as db_attendance
from src.db import classroom as db_classroom
from .errores import SIN_ACCESO

FULL_ASISTENCIA = 100
FULL_INASISTENCIA = 0
QR_EXPIRADO = {"error": "El código QR es inválido o ha expirado. Solicite uno nuevo al profesor.", "status": 400}
ALUMNO_NO_ENCONTRADO = {"error": "El padrón/DNI no pertenece a la nómina de este curso.", "status": 404}

def obtener_inasistencias_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    total_eventos = db_attendance.contar_eventos_classroom(classroom_id)
    alumnos = db_attendance.obtener_inasistencias_por_alumno(classroom_id)

    if total_eventos == 0 or not alumnos:
        porcentaje_asistencia = FULL_ASISTENCIA
        inasistencias_promedio = FULL_INASISTENCIA
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

def obtener_datos_qr(token: str) -> tuple:
    evento = db_attendance.obtener_evento_por_token(token)
    if not evento:
        return None, QR_EXPIRADO
        
    clase_data = {
        "materia": evento["materia"],
        "docente": evento["docente"],
        "fecha": evento["fecha"]
    }
    return clase_data, None


def procesar_registro_presente(token: str, padron: str) -> tuple:
    if not padron or not token:
        return None, {"error": "Faltan datos obligatorios.", "status": 400}
    
    evento = db_attendance.obtener_evento_por_token(token)
    if not evento:
        return None, QR_EXPIRADO
    
    student_id = db_attendance.obtener_alumno_por_padron_aula(evento["classroom_id"], padron)
    if not student_id:
        return None, ALUMNO_NO_ENCONTRADO
    
    db_attendance.registrar_presente_db(student_id, evento["event_id"])
    return {"message": "¡Presente registrado exitosamente!"}, None