from flask import Blueprint, jsonify, request

from src.funciones.auth import crear_token, validar_credenciales
from src.funciones.errores import (
    EMAIL_REQUERIDO,
    PASSWORD_REQUERIDO,
    USER_ID_NO_COINCIDE,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
def login(user_id: int):
    email = request.args.get("email")
    password = request.args.get("password")

    if not email:
        return jsonify(EMAIL_REQUERIDO), EMAIL_REQUERIDO["status"]

    if not password:
        return jsonify(PASSWORD_REQUERIDO), PASSWORD_REQUERIDO["status"]

    usuario, error = validar_credenciales(email, password)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    if usuario["id"] != user_id:
        return jsonify(USER_ID_NO_COINCIDE), USER_ID_NO_COINCIDE["status"]

    token = crear_token(
        usuario["id"],
        usuario["username"],
        usuario["email"],
    )

    return (
        jsonify(
            {
                "id": usuario["id"],
                "username": usuario["username"],
                "email": usuario["email"],
                "role_id": usuario["role_id"],
                "token": token,
            }
        ),
        200,
    )
