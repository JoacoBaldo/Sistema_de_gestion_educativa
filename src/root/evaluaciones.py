from flask import Blueprint, jsonify
from src.funciones.evaluaciones import crear_evaluacion

evaluacion_bp = Blueprint("evaluacion", __name__)

@evaluacion_bp.route('api/v1/classroom/<int:classroom_id>/evaluaciones', methods=['POST'])
def crear_evaluacion_root(classroom_id: int, fecha: str, aulas: tuple):
    resultado, error = crear_evaluacion(classroom_id, fecha, aulas)
    
    if error:
        return jsonify({"error": error}), 400
    
    return jsonify(resultado), resultado.get("status_code", 500)


