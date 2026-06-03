import csv
import io
from src.db.evaluaciones import eliminar_evaluacion_db, insertar_notas_csv_db
from src.db.evaluaciones import crear_evaluacion_db, existe_classroom
from .errores import (
    ARCHIVO_INVALIDO,
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


def eliminar_evaluacion(eval_id: int) -> tuple:
    eliminar_evaluacion_db(eval_id)
    return {"message": f"La evaluación {eval_id} fue eliminada exitosamente."}, None


def procesar_notas_csv(eval_id: int, file) -> tuple:
    if not file or file.filename == '':
        return None, ARCHIVO_INVALIDO
        
    if not file.filename.endswith('.csv'):
        return None, ARCHIVO_INVALIDO
        
    stream = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
    csv_reader = csv.reader(stream)
    
    registros = []
    for row in csv_reader:
        if len(row) >= 2: 
            registros.append({"padron": row[0], "nota": row[1]})
            
    cantidad_insertadas = insertar_notas_csv_db(eval_id, registros)
    
    return {
        "message": f"Se procesaron {cantidad_insertadas} notas exitosamente.",
        "data": registros
    }, None