from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from src.funciones.auth import (
    datos_completos,
    buscar_token,
    usuario_existe,
    actualizar_contrasenia,
)

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/actualizar-contrasenia", methods=["POST"])
def actualizar_contrasenia():

    token, nueva_contrasenia, error = datos_completos()

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    token_activo, error = buscar_token(token)
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

    id_usuario, error = usuario_existe(token_activo.usuario_id)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    hash_generado = generate_password_hash(nueva_contrasenia)

    resultado = actualizar_contrasenia(id_usuario, hash_generado)

    return jsonify{resultado}, 200
