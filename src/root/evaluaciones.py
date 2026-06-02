from flask import Blueprint, jsonify
from src.funciones.evaluaciones import crear_evaluacion, eliminar_evaluacion

user_bp = Blueprint("user", __name__)


@user_bp.route("api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["POST"])
def crear_evaluacion_root(classroom_id: int, fecha: str, aulas: tuple):
    resultado, error = crear_evaluacion(classroom_id, fecha, aulas)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado), resultado.get("status_code", 500)


@user_bp.route("api/v1/evaluaciones/<int:evaluacion_id>", methods=["DELETE"])
def eliminar_evaluacion_root(evaluacion_id: int):
    resultado, error = eliminar_evaluacion(evaluacion_id)

    if error:
        return jsonify({"error": error}), 400

    return jsonify(resultado), resultado.get("status_code", 500)
