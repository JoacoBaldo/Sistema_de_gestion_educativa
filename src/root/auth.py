from flask import Blueprint, jsonify, request

from src.funciones.auth import crear_token, login_con_link, validar_credenciales
from src.funciones.errores import (
    DATOS_USUARIO_REQUERIDOS,
    EMAIL_REQUERIDO,
    LINK_INVALIDO,
    PASSWORD_REQUERIDO,
)
from src.funciones.user import create_user

from .utils import responder_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/login/join", methods=["POST"])
def login_join():
    join_token = request.args.get("token")
    if not join_token:
        return responder_error(LINK_INVALIDO)

    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email:
        return responder_error(EMAIL_REQUERIDO)

    if not password:
        return responder_error(PASSWORD_REQUERIDO)

    resultado, error = login_con_link(email, password, join_token)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@auth_bp.route("/api/v1/users/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email:
        return responder_error(EMAIL_REQUERIDO)

    if not password:
        return responder_error(PASSWORD_REQUERIDO)

    usuario, error = validar_credenciales(email, password)

    if error:
        return responder_error(error)

    token = crear_token(usuario)

    return (
        jsonify(
            {
                "id": usuario["id"],
                "username": usuario["username"],
                "email": usuario["email"],
                "token": token,
            }
        ),
        200,
    )


@auth_bp.route("/api/v1/register", methods=["POST"])
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
