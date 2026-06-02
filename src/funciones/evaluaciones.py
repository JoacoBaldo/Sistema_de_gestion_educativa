from src.db.evaluaciones import crear_evaluacion_db, existe_classroom
from src.funciones.errores import CLASSROOM_NO_EXISTE, FECHA_NO_VALIDA, AULA_NO_VALIDA
from src.db.evaluaciones import eliminar_evaluacion_db, existe_evaluacion


def crear_evaluacion(classroom_id: int, fecha: str, aulas: tuple):
    if not classroom_id or not fecha or not aulas:
        return {"error": "Faltan datos obligatorios", "status_code": 400}
    if not existe_classroom(classroom_id):
        return CLASSROOM_NO_EXISTE
    if not fecha_es_valida(fecha):
        return FECHA_NO_VALIDA
    if not aula_es_valida(aulas):
        return AULA_NO_VALIDA
    return crear_evaluacion_db(classroom_id, fecha, aulas)


def fecha_es_valida(fecha):
    if not isinstance(fecha, str):
        return False


def aula_es_valida(aulas):
    for aula in aulas:
        if (
            aula not in AULAS_VALIDAS
        ):  # Las aulas validas debe ser una lista que defina las aulas que
            # la catedra puede asignar a las evaluaciones.
            return False
    return True


def eliminar_evaluacion(evaluacion_id):
    if not evaluacion_id:
        return {"error": "Falta el ID de la evaluación", "status_code": 400}
    if not existe_evaluacion(evaluacion_id):
        return {"error": "La evaluación especificada no existe", "status_code": 404}
    return eliminar_evaluacion_db(evaluacion_id)
