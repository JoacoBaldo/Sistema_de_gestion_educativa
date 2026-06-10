from src.db.classroom import existe_classroom
from src.db.evaluaciones import (
    actualizar_evaluacion_db,
    crear_evaluacion_db,
    existe_evaluacion_en_classroom,
    existe_evaluation_type,
    obtener_evaluacion_por_id,
    obtener_evaluaciones_classroom,
)

from .errores import (
    CLASSROOM_NO_EXISTE,
    DATOS_EVALUACION_REQUERIDOS,
    REFERENCED_EVAL_NO_EXISTE,
    REFERENCED_EVAL_REQUERIDO,
    TIPO_EVALUACION_INVALIDO,
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
        return None, {
            "error": "La evaluación especificada no existe",
            "status": 404,
        }

    if classroom_id is not None and not existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if evaluation_type_id is not None and not existe_evaluation_type(
        evaluation_type_id
    ):
        return None, TIPO_EVALUACION_INVALIDO

    new_classroom_id = (
        classroom_id if classroom_id is not None else evaluacion_actual["classroom_id"]
    )
    new_evaluation_type_id = (
        evaluation_type_id
        if evaluation_type_id is not None
        else evaluacion_actual["evaluation_type_id"]
    )

    if new_evaluation_type_id == EVALUATION_TYPE_RECUPERATORIO:
        if referenced_eval_id is None:
            if evaluacion_actual["evaluation_type_id"] != EVALUATION_TYPE_RECUPERATORIO:
                return None, REFERENCED_EVAL_REQUERIDO
            referenced_eval_id = evaluacion_actual["referenced_eval_id"]

        if referenced_eval_id is not None:
            if not existe_evaluacion_en_classroom(
                referenced_eval_id,
                new_classroom_id,
            ):
                return None, REFERENCED_EVAL_NO_EXISTE
    else:
        referenced_eval_id = None

    resultado = actualizar_evaluacion_db(
        classroom_id,
        name,
        evaluation_type_id,
        referenced_eval_id,
        individual,
        evaluation_id,
    )
    return resultado, None
