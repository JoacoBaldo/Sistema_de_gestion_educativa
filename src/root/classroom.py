from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.classroom import (
    crear_nueva_classroom,
    eliminar_usuario_classroom,
    obtener_link_classroom,
    obtener_lista_classrooms,
    obtener_evaluaciones_classroom,
    obtener_periodos_academicos,
    obtener_profesores_classroom,
)
from src.funciones.errores import (
    DATOS_INVALIDOS,
    ROLE_ID_REQUERIDO,
    USER_ID_NO_COINCIDE,
)
from .utils import extraer_token, responder_error

classroom_bp = Blueprint("classroom", __name__)


@classroom_bp.route("/api/v1/classrooms/<int:classroom_id>/professors", methods=["GET"])
def listar_profesores(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_profesores_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@classroom_bp.route(
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


@classroom_bp.route("/api/v1/classrooms/<int:classroom_id>/link", methods=["GET"])
def obtener_link(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    role_id = request.args.get("role_id")
    if role_id is None:
        return responder_error(ROLE_ID_REQUERIDO)

    try:
        role_id = int(role_id)
    except ValueError:
        return responder_error(ROLE_ID_REQUERIDO)

    resultado, error = obtener_link_classroom(classroom_id, usuario["id"], role_id)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@classroom_bp.route("/api/v1/academic-periods", methods=["GET"])
def listar_periodos_academicos():
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_periodos_academicos()
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@classroom_bp.route("/api/v1/classrooms/<int:user_id>", methods=["GET"])
def obtener_classrooms(user_id: int):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    if usuario["id"] != user_id:
        return responder_error(USER_ID_NO_COINCIDE)

    resultado, error = obtener_lista_classrooms(user_id)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@classroom_bp.route("/api/v1/classrooms", methods=["POST"])
def crear_aula():
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    name = body.get("name")
    department = body.get("department")
    university = body.get("university")

    if not name or not department or not university:
        return responder_error(DATOS_INVALIDOS)

    resultado, error = crear_nueva_classroom(
        name, department, university, usuario["id"]
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 201


@classroom_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/evaluaciones", methods=["GET"]
)
def listar_evaluaciones(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    resultado, error = obtener_evaluaciones_classroom(classroom_id, usuario["id"])

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200
