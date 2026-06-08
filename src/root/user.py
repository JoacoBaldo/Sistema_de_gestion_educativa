from flask import Blueprint, jsonify

from src.funciones.auth import verificar_token
from src.funciones.classroom import (
    eliminar_usuario_classroom,
    obtener_profesores_classroom,
)
from .utils import extraer_token, responder_error

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/classrooms/<int:classroom_id>/professors", methods=["GET"])
def listar_profesores(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_profesores_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/user/<int:user_id>", methods=["DELETE"]
)
def eliminar_usuario(classroom_id, user_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_usuario_classroom(classroom_id, user_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
