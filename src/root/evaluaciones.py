from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.evaluaciones import crear_evaluacion
from .utils import extraer_token, responder_error

evaluacion_bp = Blueprint("evaluacion", __name__)


@evaluacion_bp.route(
    "/api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["POST"]
)
def crear_evaluacion_root(classroom_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}

    name = body.get("name")
    if not isinstance(name, str):
        name = ""

    evaluation_type_raw = body.get("evaluation_type_id")
    try:
        evaluation_type_id = int(evaluation_type_raw)
    except (TypeError, ValueError):
        evaluation_type_id = 0

    referenced_eval_raw = body.get("referenced_eval_id")
    try:
        referenced_eval_id = int(referenced_eval_raw) if referenced_eval_raw is not None else None
    except (TypeError, ValueError):
        referenced_eval_id = None

    individual_raw = body.get("individual", 1)
    try:
        individual = int(individual_raw)
    except (TypeError, ValueError):
        individual = 1

    resultado, error = crear_evaluacion(
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]
