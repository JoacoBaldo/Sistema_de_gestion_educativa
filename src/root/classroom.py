from flask import Blueprint, jsonify, request, g
from src.funciones.auth import token_required
from src.funciones.classroom import (
    obtener_profesores_classroom,
    eliminar_usuario_classroom,
    obtener_link_classroom,
    obtener_lista_classrooms,
)

classroom_bp = Blueprint("classroom", __name__)


@classroom_bp.route("/api/v1/classrooms/<int:classroom_id>/professors", methods=["GET"])
@token_required
def listar_profesores(classroom_id):
    usuario = g.current_user
    resultado, error = obtener_profesores_classroom(classroom_id, usuario["id"])

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200


@classroom_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/user/<int:user_id>", methods=["DELETE"]
)
@token_required
def eliminar_usuario(classroom_id, user_id):
    usuario = g.current_user
    resultado, error = eliminar_usuario_classroom(classroom_id, user_id, usuario["id"])

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200


@classroom_bp.route("/api/v1/classrooms/<int:classroom_id>/link", methods=["GET"])
@token_required
def obtener_link(classroom_id):
    usuario = g.current_user
    body = request.get_json(silent=True) or {}
    role_id = body.get("role_id")

    if role_id is None:
        return jsonify({"error": "role_id es requerido"}), 400

    resultado, error = obtener_link_classroom(classroom_id, usuario["id"], role_id)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200


@classroom_bp.route("/api/v1/classrooms/<user_id>", methods=["GET"])
def obtener_classrooms(user_id: int):
    token = _extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return jsonify({"error": error["error"]}), error["status"]

    resultado, error = obtener_lista_classrooms(user_id)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200
