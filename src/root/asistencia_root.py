from flask import Blueprint
from src.funciones.asistencia import sumar_inasistencia

asistencia_bp = Blueprint('asistencia_root', __name__)

@asistencia_bp.route('/sumar_inasistencia/<int:classroom_id>', methods=['POST'])
def inasistencia_root(classroom_id):
    if not classroom_id:
        return {"error": "El ID del aula es requerido"}, 400
    return sumar_inasistencia(classroom_id)