from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash
from src.funciones.auth import datos_completos

auth_bp = Blueprint("auth", __name__)


@app.route('/api/auth/actualizar-contrasenia', methods=['POST'])
def actualizar_contrasenia():
    
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

    resultado = actualizar_contrasenia(id_usuario, hash_generado)

    return jsonify({resultado}), 200

