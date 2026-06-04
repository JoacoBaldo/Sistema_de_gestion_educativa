from flask import Blueprint, jsonify, request

from src.funciones.auth import crear_token, login_con_link, validar_credenciales
from src.funciones.errores import (
    EMAIL_REQUERIDO,
    LINK_INVALIDO,
    PASSWORD_REQUERIDO,
    USER_ID_NO_COINCIDE,
)
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


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["POST"])
def login(user_id: int):
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

    if usuario["id"] != user_id:
        return responder_error(USER_ID_NO_COINCIDE)

    token = crear_token(usuario["id"], usuario["username"], usuario["email"])

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
