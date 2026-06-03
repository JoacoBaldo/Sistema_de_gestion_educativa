from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.evaluaciones import crear_evaluacion, eliminar_evaluacion, procesar_notas_csv
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
    fecha = body.get("fecha")
    aulas = body.get("aulas")

    resultado, error = crear_evaluacion(classroom_id, fecha, aulas)
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route("/api/v1/evaluations/<int:eval_id>", methods=["DELETE"])
def delete_evaluacion(eval_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_evaluacion(eval_id)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@evaluacion_bp.route("/api/v1/evaluations/<int:eval_id>/grades/csv", methods=["POST"])
def upload_csv_grades(eval_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    if 'file' not in request.files:
        return responder_error({"error": "No se proporcionó ningún archivo en el form-data", "status": 400})

    file = request.files['file']
    
    resultado, error = procesar_notas_csv(eval_id, file)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200