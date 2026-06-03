from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.errores import DATOS_USUARIO_REQUERIDOS, EMAIL_REQUERIDO
from src.funciones.user import create_user, send_password_mail, actualizar_alumno_db, crear_alumno_db
from .utils import extraer_token, responder_error


user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/create_user", methods=["POST"])
def create_user_route():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return responder_error(DATOS_USUARIO_REQUERIDOS)

    resultado, error = create_user(
        {"username": username, "email": email, "password": password}
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]


@user_bp.route("/recuperar-password", methods=["POST"])
def solicitar_recuperacion():
    data = request.get_json(silent=True) or {}
    email_usuario = data.get("email")

    if not email_usuario:
        return responder_error(EMAIL_REQUERIDO)

    resultado, error = send_password_mail(email_usuario)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route("/api/v1/students/<int:user_id>", methods=["PUT"])
def update_student(user_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    resultado, error = actualizar_alumno_db(user_id, data, usuario.get("role_id"))
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route("/api/v1/students", methods=["POST"])
def post_student():
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    resultado, error = crear_alumno_db(data, usuario.get("role_id"))
    if error:
        return responder_error(error)

    return jsonify(resultado), 201