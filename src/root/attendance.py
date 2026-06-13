from flask import Blueprint, jsonify, request
from src.funciones.attendance import (
    enviar_qr_a_estudiantes,
    obtener_inasistencias_classroom,
    sumar_inasistencia,
    validar_asistencia,
)
from src.funciones.auth import verificar_token
from src.funciones.errores import CODIGO_REQUERIDO, DELTA_CERO, DELTA_INVALIDO

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
def registrar_asistencia_aula(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    delta = body.get("delta", 1)

    try:
        delta = int(delta)
    except (ValueError, TypeError):
        return responder_error(DELTA_INVALIDO)

    if delta == 0:
        return responder_error(DELTA_CERO)

    resultado, error = sumar_inasistencia(
        classroom_id, delta=delta, usuario_id=usuario["id"]
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@attendance_bp.route("/api/v1/attendance/<int:classroom_id>/qr", methods=["POST"])
def enviar_qr_estudiantes(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = enviar_qr_a_estudiantes(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@attendance_bp.route("/api/v1/attendance/<int:classroom_id>/validar", methods=["POST"])
def validar_asistencia_alumno_api(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    code = body.get("code")

    if not code:
        return responder_error(CODIGO_REQUERIDO)

    resultado, error = validar_asistencia(classroom_id, code, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
