from flask import Blueprint, request, jsonify
from src.funciones.user import (
    change_password_mail,
    create_user,
)

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

    if not email_usuario:
        return jsonify({"error": "El email es obligatorio"}), 400

    token_generado = "12345abcde-token-de-prueba"
    link_falso = f"http://tusitioweb.com/reset-password?token={token_generado}"

    exito = change_password_mail(email_usuario, link_falso)

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
