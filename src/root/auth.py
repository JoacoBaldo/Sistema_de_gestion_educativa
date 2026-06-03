from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from src.funciones.auth import (
    datos_completos,
    buscar_token,
    usuario_existe,
    actualizar_contrasenia,
)
from .utils import responder_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/actualizar-contrasenia", methods=["POST"])
def actualizar_contrasenia():

    token, nueva_contrasenia, error = datos_completos()

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    token_activo, error = buscar_token(token)
    
@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
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
                "role_id": usuario["role_id"],
                "token": token,
            }
        ),
        200,
    )
