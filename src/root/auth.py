from flask import Blueprint, jsonify, request

from src.funciones.auth import crear_token, validar_credenciales

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
def login(user_id: int):
    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email:
        return jsonify({"error": "email es requerido"}), 400

    if not password:
        return jsonify({"error": "password es requerido"}), 400

    usuario, error = validar_credenciales(email, password)
    if error:
        return jsonify({"error": error["error"]}), error["status"]

    if usuario["id"] != user_id:
        return jsonify({"error": "user_id no coincide"}), 400

    token = crear_token(usuario["id"], usuario["username"], usuario["email"])

    return jsonify({
        "id": usuario["id"],
        "username": usuario["username"],
        "email": usuario["email"],
        "role_id": usuario["role_id"],
        "token": token,
    }), 200
