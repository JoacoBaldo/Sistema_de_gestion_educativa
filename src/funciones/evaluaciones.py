from src.db.evaluaciones import (
    crear_evaluacion_db,
    existe_evaluation_type,
    existe_evaluacion_en_classroom,
)
from src.db.classroom import existe_classroom
from .errores import (
    CLASSROOM_NO_EXISTE,
    DATOS_EVALUACION_REQUERIDOS,
    REFERENCED_EVAL_NO_EXISTE,
    REFERENCED_EVAL_REQUERIDO,
    TIPO_EVALUACION_INVALIDO,
)

EVALUATION_TYPE_RECUPERATORIO = 3


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
