from flask import Blueprint, request, jsonify
from src.funciones.user import (
    change_password_mail,
    create_user,
)
from src.db.user import get_user_id_by_email

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

    result = create_user(user_data)
    return jsonify(result), result["status_code"]
