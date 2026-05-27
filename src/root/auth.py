from flask import Blueprint, jsonify
from werkzeug.security import generate_password_hash
from src.funciones.auth import (
    datos_completos,
    buscar_token,
    usuario_existe,
    actualizar_contrasenia)
    
auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/auth/actualizar-contrasenia", methods=["POST"])
def actualizar_contrasenia_handler():

    token, nueva_contrasenia, error = datos_completos()

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    token_activo, error = buscar_token(token)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    id_usuario, error = usuario_existe(token_activo.usuario_id)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    hash_generado = generate_password_hash(nueva_contrasenia)

<<<<<<< HEAD
    resultado = actualizar_contrasenia_db(id_usuario, hash_generado)
=======
    resultado = actualizar_contrasenia(id_usuario, nueva_contrasenia)
>>>>>>> 0ec54a3 (needed changes)

    return jsonify({resultado}), 200
