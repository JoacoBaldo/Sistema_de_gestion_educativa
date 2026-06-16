from src.db.classroom import existe_classroom
from src.db.evaluations import (
    actualizar_evaluacion_db,
    actualizar_nota_estudiante_db,
    crear_evaluacion_db,
    eliminar_nota_estudiante_db,
    existe_evaluacion_en_classroom,
    existe_evaluation_type,
    obtener_evaluacion_por_id,
    obtener_evaluaciones_classroom,
    eliminar_evaluacion_db,
    procesar_notas_masivas_db,
    evaluacion_tiene_notas_db,
    guardar_nota_individual_o_equipo_db,
)

from .errores import (
    CLASSROOM_NO_EXISTE,
    DATOS_EVALUACION_REQUERIDOS,
    REFERENCED_EVAL_NO_EXISTE,
    REFERENCED_EVAL_REQUERIDO,
    TIPO_EVALUACION_INVALIDO,
    EVALUACION_NO_EXISTE,
)

EVALUATION_TYPE_RECUPERATORIO = 3


def obtener_evaluaciones(classroom_id: int) -> tuple:
    if not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE
    return obtener_evaluaciones_classroom(classroom_id), None


def crear_evaluacion(
    classroom_id: int,
    name: str,
    evaluation_type_id: int,
    referenced_eval_id: int | None,
    individual: int,
    due_date: str | None,
) -> tuple:
    if not name or not evaluation_type_id:
        return None, DATOS_EVALUACION_REQUERIDOS

    if not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if not existe_evaluation_type(evaluation_type_id):
        return None, TIPO_EVALUACION_INVALIDO

    if evaluation_type_id == EVALUATION_TYPE_RECUPERATORIO:
        if not referenced_eval_id:
            return None, REFERENCED_EVAL_REQUERIDO
        if not existe_evaluacion_en_classroom(referenced_eval_id, classroom_id):
            return None, REFERENCED_EVAL_NO_EXISTE
    else:
        referenced_eval_id = None

    resultado = crear_evaluacion_db(
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual, due_date
    )
    return resultado, None


def _resolver_referenced_eval(
    new_type_id: int,
    referenced_eval_id: int | None,
    evaluacion_actual: dict,
) -> tuple[int | None, dict | None]:
    if new_type_id != EVALUATION_TYPE_RECUPERATORIO:
        return None, None

    if referenced_eval_id is not None:
        return referenced_eval_id, None

    if evaluacion_actual["evaluation_type_id"] != EVALUATION_TYPE_RECUPERATORIO:
        return None, REFERENCED_EVAL_REQUERIDO

    return evaluacion_actual["referenced_eval_id"], None


def actualizar_evaluacion(
    classroom_id: int | None,
    name: str | None,
    evaluation_type_id: int | None,
    referenced_eval_id: int | None,
    individual: int | None,
    due_date: str | None, # Agregado aquí
    evaluation_id: int,
):
    if (classroom_id is None and name is None and evaluation_type_id is None 
            and referenced_eval_id is None and individual is None and due_date is None):
        return None, DATOS_EVALUACION_REQUERIDOS

    evaluacion_actual = obtener_evaluacion_por_id(evaluation_id)
    if evaluacion_actual is None:
        return None, EVALUACION_NO_EXISTE

    if evaluacion_tiene_notas_db(evaluation_id):
        return None, {"error": "No se puede modificar la evaluación porque ya tiene calificaciones asignadas", "status": 400}

    return actualizar_evaluacion_db(
        classroom_id,
        name,
        evaluation_type_id,
        referenced_eval_id,
        individual,
        due_date, # Pasado a la DB
        evaluation_id,
    ), None


def eliminar_evaluacion(evaluation_id: int) -> tuple:
    try:
        evaluacion = obtener_evaluacion_por_id(evaluation_id)
        if evaluacion is None:
            return None, {
                "error": "La evaluación especificada no existe",
                "status": 404,
            }

        resultado = eliminar_evaluacion_db(evaluation_id)
        return resultado, None

    except Exception as e:
        error_estructurado = {
            "error": f"ERROR_BASE_DE_DATOS: {str(e)}",
            "status": 500,
        }
        return None, error_estructurado


def cargar_notas_masivas_logic(
    classroom_id: int, evaluation_id: int, grades: list[dict]
) -> tuple[dict, dict | None]:
    if not grades:
        return {}, {
            "error": "La lista de notas está vacía o el CSV no tenía datos válidos.",
            "status": 400,
        }

    if not classroom_id or not evaluation_id:
        return {}, {"error": "Faltan parámetros de aula o evaluación.", "status": 400}

    resultado = procesar_notas_masivas_db(classroom_id, evaluation_id, grades)

    if resultado.get("error"):
        return {}, {
            "error": f"Error en base de datos: {resultado['error']}",
            "status": 500,
        }

    return {"inserted": resultado.get("inserted", 0)}, None

def actualizar_nota_estudiante(evaluation_id: int, user_id: int, score: float) -> tuple:
    if score is None:
        return None, {"error": "La calificación es requerida", "status": 400}
        
    if not obtener_evaluacion_por_id(evaluation_id):
        return None, EVALUACION_NO_EXISTE

    resultado = actualizar_nota_estudiante_db(evaluation_id, user_id, float(score))
    return resultado, None


def eliminar_nota_estudiante(evaluation_id: int, user_id: int) -> tuple:
    if not obtener_evaluacion_por_id(evaluation_id):
        return None, EVALUACION_NO_EXISTE
        
    resultado = eliminar_nota_estudiante_db(evaluation_id, user_id)
    return resultado, None

def crear_nota_individual_o_grupal(evaluation_id: int, score: float, user_id: int | None = None, team_id: int | None = None) -> tuple:
    if score is None:
        return None, {"error": "La calificación es requerida", "status": 400}
        
    evaluacion = obtener_evaluacion_por_id(evaluation_id)
    if not evaluacion:
        return None, EVALUACION_NO_EXISTE
        
    es_individual = bool(evaluacion.get("individual"))
    
    if es_individual:
        if not user_id:
            return None, {"error": "Esta evaluación es de tipo individual. Debe especificar un alumno (user_id).", "status": 400}
        team_id = None
    else:
        if not team_id:
            return None, {"error": "Esta evaluación es de tipo grupal. Debe especificar un equipo (team_id).", "status": 400}
        user_id = None

    resultado = guardar_nota_individual_o_equipo_db(evaluation_id, float(score), user_id, team_id)
    return resultado, None
