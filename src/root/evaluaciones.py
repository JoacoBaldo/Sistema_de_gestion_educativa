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
    name: str | None = body.get("name")
    evaluation_type_id: int | None = body.get("evaluation_type_id")
    referenced_eval_id: int | None = body.get("referenced_eval_id")
    individual = body.get("individual", 1)

    resultado, error = crear_evaluacion(
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual  # type: ignore[arg-type]
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]
