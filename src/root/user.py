from flask import Blueprint, request, jsonify
from src.funciones.user import (
    change_password_mail,
    change_password_db,
    create_user,
)

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/change_password_mail", methods=["GET"])
def change_password_mail_route():
    data = request.get_json()
    email = data.get("email")
    if not email:
        return jsonify({"error": "Email is required", "status_code": 400}), 400
    result = change_password_mail(email)
    return jsonify(result), result["status_code"]


@user_bp.route("/api/v1/change_password_db", methods=["PATCH"])
def change_password_db_route():
    data = request.get_json()
    email = data.get("email")
    new_password = data.get("new_password")
    if not email or not new_password:
        return jsonify(
            {"error": "Email and new password are required", "status_code": 400}
        ), 400
    result = change_password_db({"email": email, "new_password": new_password})
    return jsonify(result), result["status_code"]


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
