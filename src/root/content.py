from flask import Blueprint, jsonify, request

from src.funciones.content import (eliminar_contenido_classroom, subir_contenido_classroom)

from src.root.classroom import (
    DATOS_INVALIDOS,
    extraer_token,
    responder_error,
    verificar_token,
)

content_bp = Blueprint("content", __name__)


@content_bp.route(
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

    if not titulo or not url:
        return responder_error(DATOS_INVALIDOS)

    resultado, error = subir_contenido_classroom(
        classroom_id, titulo, url, usuario["id"]
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 201


@content_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/contenidos/<int:contenido_id>",methods=["DELETE"]
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