from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.resources import (
    eliminar_contenido_classroom,
    editar_contenido_classroom,
    listar_recursos,
    subir_contenido_classroom,
)

from .utils import extraer_token, responder_error

DATOS_INVALIDOS = "DATOS_INVALIDOS"

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


@resources_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/contenidos", methods=["POST"]
)
def subir_contenido(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    titulo = body.get("titulo")
    url = body.get("url")
    tipo = body.get("tipo")

    if not titulo or not url:
        return responder_error(DATOS_INVALIDOS)

    resultado, error = subir_contenido_classroom(
        classroom_id, titulo, url, usuario["id"], tipo
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 201


@resources_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/contenidos/<int:contenido_id>",
    methods=["DELETE"],
)
def eliminar_contenido(classroom_id, contenido_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_contenido_classroom(
        classroom_id, contenido_id, usuario["id"]
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 200

@resources_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/contenidos/<int:contenido_id>",
    methods=["PUT"],
)
def actualizar_contenido(classroom_id, contenido_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    titulo = body.get("titulo")
    tipo = body.get("tipo")
    url = body.get("url")

    if not titulo or not url or not tipo:
        return responder_error(DATOS_INVALIDOS)

    resultado, error_edit = editar_contenido_classroom(
        classroom_id, contenido_id, titulo, tipo, url, usuario["id"]
    )
    if error_edit:
        return responder_error(error_edit)

    return jsonify(resultado), 200