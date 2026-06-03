from src.db.evaluaciones import crear_evaluacion_db, existe_classroom
from .errores import (
    AULA_NO_VALIDA,
    CLASSROOM_NO_EXISTE,
    DATOS_EVALUACION_REQUERIDOS,
    FECHA_NO_VALIDA,
)

AULAS_VALIDAS = ("Aula 101", "Aula 102", "Aula 103")


def crear_evaluacion(classroom_id: int, fecha: str, aulas: tuple) -> tuple:
    if not classroom_id or not fecha or not aulas:
        return None, DATOS_EVALUACION_REQUERIDOS
    if not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE
    if not fecha_es_valida(fecha):
        return None, FECHA_NO_VALIDA
    if not aula_es_valida(aulas):
        return None, AULA_NO_VALIDA
    resultado = crear_evaluacion_db(classroom_id, fecha, aulas)
    return resultado, None


def fecha_es_valida(fecha: str) -> bool:
    if not isinstance(fecha, str):
        return False
    try:
        from datetime import datetime

        datetime.strptime(fecha, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def aula_es_valida(aulas: tuple) -> bool:
    for aula in aulas:
        if aula not in AULAS_VALIDAS:
            return False
    return True
