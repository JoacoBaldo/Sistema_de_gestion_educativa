from flask import Blueprint, jsonify
from src.funciones.resources import listar_recursos
from src.funciones.auth import verificar_token
from .utils import extraer_token, responder_error

resources_bp = Blueprint("resources", __name__)

@resources_bp.route("/api/v1/classrooms/<int:classroom_id>/resources", methods=["GET"])
def obtener_recursos_aula(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    
    if error:
        return responder_error(error)
    
    resultado, error_recursos = listar_recursos(classroom_id, usuario["id"])
    
    if error_recursos:
        return responder_error(error_recursos)
    return jsonify(resultado), 200