from src.db.classroom import existe_classroom
from src.db.evaluations import (
    actualizar_evaluacion_db,
    crear_evaluacion_db,
    existe_evaluacion_en_classroom,
    existe_evaluation_type,
    obtener_evaluacion_por_id,
    obtener_evaluaciones_classroom,
    eliminar_evaluacion_db,
    procesar_notas_masivas_db,
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
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual
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
    evaluation_id: int,
):
    if (
        classroom_id is None
        and name is None
        and evaluation_type_id is None
        and referenced_eval_id is None
        and individual is None
    ):
        return None, DATOS_EVALUACION_REQUERIDOS

    evaluacion_actual = obtener_evaluacion_por_id(evaluation_id)
    if evaluacion_actual is None:
        return None, EVALUACION_NO_EXISTE

    if classroom_id is not None and not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if evaluation_type_id is not None and not existe_evaluation_type(
        evaluation_type_id
    ):
        return None, TIPO_EVALUACION_INVALIDO

    new_classroom_id = (
        classroom_id if classroom_id is not None else evaluacion_actual["classroom_id"]
    )
    new_type_id = (
        evaluation_type_id
        if evaluation_type_id is not None
        else evaluacion_actual["evaluation_type_id"]
    )

    ref_eval_final, error = _resolver_referenced_eval(
        new_type_id, referenced_eval_id, evaluacion_actual
    )
    if error:
        return None, error

    if ref_eval_final is not None and not existe_evaluacion_en_classroom(
        ref_eval_final, new_classroom_id
    ):
        return None, REFERENCED_EVAL_NO_EXISTE

    return actualizar_evaluacion_db(
        classroom_id,
        name,
        evaluation_type_id,
        ref_eval_final,
        individual,
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



def cargar_notas_masivas_logic(classroom_id: int, evaluation_id: int, grades: list[dict]) -> tuple[dict, dict | None]:
    if not grades:
        return {}, {"error": "La lista de notas está vacía o el CSV no tenía datos válidos.", "status": 400}

    if not classroom_id or not evaluation_id:
        return {}, {"error": "Faltan parámetros de aula o evaluación.", "status": 400}

    resultado = procesar_notas_masivas_db(classroom_id, evaluation_id, grades)

    if resultado.get("error"):
        return {}, {"error": f"Error en base de datos: {resultado['error']}", "status": 500}

    return {"inserted": resultado.get("inserted", 0)}, None