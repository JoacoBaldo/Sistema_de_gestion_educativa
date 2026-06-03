from flask import Blueprint, jsonify, request

from src.funciones.auth import crear_token, validar_credenciales
from src.funciones.errores import (
    EMAIL_REQUERIDO,
    PASSWORD_REQUERIDO,
)
from .utils import responder_error

auth_bp = Blueprint("auth", __name__)


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
