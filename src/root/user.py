from flask import Blueprint, request, jsonify
from src.funciones.user import (
    change_password_mail,
    create_user, 
)
from src.db.user import get_user_id_by_email

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/create_user", methods=["POST"])
def create_user_route():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify(
            {"error": "Username, email, and password are required", "status_code": 400}
        ), 400

    user_data = {"username": username, "email": email, "password": password}

    result = create_user(user_data)
    return jsonify(result), result["status_code"]


@user_bp.route("/recuperar-password", methods=["POST"])
def solicitar_recuperacion():
    data = request.get_json()
    email_usuario = data.get("email")
    id_usuario = get_user_id_by_email(email_usuario).get("user_id")

    if not email_usuario:
        return jsonify({"error": "El email es obligatorio"}), 400
    
    if not id_usuario:
        return jsonify({"error": "El ID de usuario es obligatorio"}), 400

    exito = change_password_mail(email_usuario, id_usuario)

    if exito:
        return jsonify(
            {
                "mensaje": "Se envió un mail con las instrucciones para recuperar la contraseña."
            }
        ), 200
    else:
        return jsonify(
            {"error": "Hubo un problema interno al intentar enviar el correo."}
        ), 500
