from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.evaluaciones import crear_evaluacion, actualizar_evaluacion
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
    evaluation_type_id = body.get("evaluation_type_id")
    referenced_eval_id = body.get("referenced_eval_id")
    individual = body.get("individual", 1)

    resultado, error = crear_evaluacion(
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route("/api/v1/evaluaciones/<int:evaluation_id>", methods=["PATCH"])
def actualizar_evaluacion_root(evaluation_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    classroom_id = body.get("classroom_id")
    name = body.get("name")
    evaluation_type_id = body.get("evaluation_type_id")
    referenced_eval_id = body.get("referenced_eval_id")
    individual = body.get("individual")

    resultado, error = actualizar_evaluacion(
        classroom_id,
        name,
        evaluation_type_id,
        referenced_eval_id,
        individual,
        evaluation_id,
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]
