from flask import Blueprint, jsonify, request

from src.db.conexion import obtener_conexion
from src.funciones.auth import crear_token, _validar_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/users/<int:user_id>", methods=["GET"])
def obtener_usuario(user_id):
    email = request.args.get("email")
    password = request.args.get("password")

    if not email or not password:
        return jsonify({"error": "email y password son requeridos"}), 400

    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT id, username, email, password, role_id
            FROM users
            WHERE id = %s AND email = %s
            LIMIT 1
            """,
            (user_id, email),
        ).fetchone()

    if not resultado:
        return jsonify({"error": "Credenciales inválidas"}), 401

    usuario_id, username_db, email_db, password_hash, role_id = resultado
    if not _validar_password(password, password_hash):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = crear_token(usuario_id, username_db, email_db)
    return jsonify({
        "id": usuario_id,
        "username": username_db,
        "email": email_db,
        "role_id": role_id,
        "token": token,
    }), 200
