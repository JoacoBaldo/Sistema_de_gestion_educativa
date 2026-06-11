from flask import Blueprint, jsonify, request
from src.funciones.attendance import obtener_inasistencias_classroom, sumar_inasistencia
from src.funciones.auth import verificar_token

from .utils import extraer_token, responder_error

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/v1/attendance/<int:classroom_id>", methods=["GET"])
def listar_inasistencias(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_inasistencias_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@attendance_bp.route("/api/v1/attendance/<int:classroom_id>", methods=["POST"])
def registrar_inasistencia(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    if not classroom_id:
        return {"error": "El ID del aula es requerido"}, 400

    body = request.get_json()
    if not body or "delta" not in body:
        return {"error": "El campo 'delta' es requerido"}, 400

    try:
        delta = int(body["delta"])
    except (ValueError, TypeError):
        return {"error": "El campo 'delta' debe ser un entero"}, 400

    if delta == 0:
        return {"error": "El campo 'delta' no puede ser 0"}, 400

    return sumar_inasistencia(classroom_id, delta=delta, usuario_id=usuario["id"])
