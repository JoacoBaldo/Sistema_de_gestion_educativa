from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.evaluations import (
    cargar_notas_masivas_logic,
    obtener_evaluaciones,
    actualizar_evaluacion,
    crear_evaluacion,
    eliminar_evaluacion,
)

from .utils import extraer_token, responder_error

evaluacion_bp = Blueprint("evaluacion", __name__)


@evaluacion_bp.route(
    "/api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["GET"]
)
def listar_evaluaciones_aula(classroom_id):
    token = extraer_token()
    usuario, error_token = verificar_token(token)
    if error_token:
        return responder_error(error_token)

    evaluaciones, error = obtener_evaluaciones(classroom_id)

    if error:
        return responder_error(error)

    return jsonify(evaluaciones), 200


@evaluacion_bp.route(
    "/api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["POST"]
)
def crear_evaluacion_root(classroom_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    if request.is_json:
        body = request.get_json(silent=True) or {}
    else:
        body = request.form or {}

    name = body.get("name") or body.get("nombre")
    if not isinstance(name, str):
        name = ""

    evaluation_type_raw = body.get("evaluation_type_id") or body.get("tipo")
    try:
        evaluation_type_id = (
            int(evaluation_type_raw) if evaluation_type_raw is not None else 0
        )
    except (TypeError, ValueError):
        evaluation_type_id = 0

    referenced_eval_raw = body.get("referenced_eval_id")
    try:
        referenced_eval_id = (
            int(referenced_eval_raw) if referenced_eval_raw is not None else None
        )
    except (TypeError, ValueError):
        referenced_eval_id = None

    individual_raw = body.get("individual", 1)
    try:
        individual = int(individual_raw)
    except (TypeError, ValueError):
        individual = 1

    if not isinstance(evaluation_type_id, int) or evaluation_type_id == 0:
        return responder_error({"mensaje": "evaluation_type_id requerido"})

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

    if request.is_json:
        body = request.get_json(silent=True) or {}
    else:
        body = request.form or {}

    classroom_id = body.get("classroom_id")
    name = body.get("name") or body.get("nombre")

    evaluation_type_raw = body.get("evaluation_type_id") or body.get("tipo")
    try:
        evaluation_type_id = (
            int(evaluation_type_raw) if evaluation_type_raw is not None else None
        )
    except (TypeError, ValueError):
        evaluation_type_id = None

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


@evaluacion_bp.route("/api/v1/evaluaciones/<int:evaluation_id>", methods=["DELETE"])
def eliminar_evaluacion_root(evaluation_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error_del = eliminar_evaluacion(evaluation_id)
    if error_del:
        return responder_error(error_del)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route(
    "/api/v1/evaluations/<int:evaluation_id>/bulk-grades", methods=["POST"]
)
def api_bulk_grades(evaluation_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    classroom_id = body.get("classroom_id")
    grades = body.get("grades", [])

    if not classroom_id:
        return responder_error(
            {"error": "El classroom_id es requerido en el payload.", "status": 400}
        )

    resultado, err = cargar_notas_masivas_logic(classroom_id, evaluation_id, grades)

    if err:
        return responder_error(err)

    return jsonify(resultado), 200
