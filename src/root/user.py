from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.classroom import (
    eliminar_usuario_classroom,
    obtener_profesores_classroom,
)
from src.funciones.errores import EMAIL_REQUERIDO, PASSWORD_REQUERIDO, TOKEN_REQUERIDO
from src.funciones.user import restablecer_password, send_password_mail

from .utils import extraer_token, responder_error

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/classrooms/<int:classroom_id>/professors", methods=["GET"])
def listar_profesores(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_profesores_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/user/<int:user_id>", methods=["DELETE"]
)
def eliminar_usuario(classroom_id, user_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_usuario_classroom(classroom_id, user_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route("/api/v1/forgot-password", methods=["POST"])
def solicitar_recuperacion():
    data = request.get_json(silent=True) or {}
    email_usuario = data.get("email")

    if not email_usuario:
        return responder_error(EMAIL_REQUERIDO)

    resultado, error = send_password_mail(email_usuario)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route("/api/v1/users/password", methods=["PATCH"])
def restablecer_contrasena():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    password = data.get("password")

    if not token:
        return responder_error(TOKEN_REQUERIDO)
    if not password:
        return responder_error(PASSWORD_REQUERIDO)

    resultado, error = restablecer_password(token, password)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
