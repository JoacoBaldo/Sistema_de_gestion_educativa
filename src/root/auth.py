from flask import Blueprint, jsonify, request
import bcrypt

from src.db.conexion import obtener_conexion
from src.funciones.auth import crear_token

auth_bp = Blueprint("auth", __name__)


def _validar_password(password: str, password_hash: str | bytes) -> bool:
    if isinstance(password_hash, str):
        password_hash = password_hash.encode("utf-8")

    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash)
    except ValueError:
        return password == password_hash.decode("utf-8", errors="ignore")


@auth_bp.route("/api/v1/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not password or not (username or email):
        return jsonify({"error": "username o email y password son requeridos"}), 400

    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT id, username, email, password
            FROM users
            WHERE username = %s OR email = %s
            LIMIT 1
            """,
            (username, email),
        ).fetchone()

    if not resultado:
        return jsonify({"error": "Credenciales inválidas"}), 401

    usuario_id, username_db, email_db, password_hash = resultado
    if not _validar_password(password, password_hash):
        return jsonify({"error": "Credenciales inválidas"}), 401

    token = crear_token(usuario_id, username_db, email_db)
    return jsonify({"access_token": token, "token_type": "Bearer"}), 200
