from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.classroom import obtener_alumnos_classroom
from src.funciones.errores import ARCHIVO_NO_ENVIADO, ARCHIVO_VACIO, DATOS_ESTUDIANTE_REQUERIDOS
from src.funciones.students import cargar_estudiantes_csv, crear_estudiante_en_classroom

from .utils import extraer_token, responder_error

students_bp = Blueprint("students", __name__)


@students_bp.route(
    "/api/v1/classrooms/<int:classroom_id>/students/import", methods=["POST"]
)
def cargar_usuarios_csv(classroom_id):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    if "archivo" not in request.files:
        return responder_error(ARCHIVO_NO_ENVIADO)

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return responder_error(ARCHIVO_VACIO)

    resultado, error = cargar_estudiantes_csv(archivo, classroom_id)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@students_bp.route("/api/v1/classrooms/<int:classroom_id>/alumnos", methods=["GET"])
def listar_alumnos_paginados(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    pagina = request.args.get("pagina", default=1, type=int)
    cantidad = request.args.get("cantidad", default=10, type=int)

    if pagina < 1 or cantidad < 1:
        return jsonify(
            {"error": "Los parámetros de paginación deben ser mayores a 0"}
        ), 400

    todos_los_alumnos, error = obtener_alumnos_classroom(classroom_id)
    if error:
        return responder_error(error)

    inicio = (pagina - 1) * cantidad
    fin = inicio + cantidad

    alumnos_paginados = todos_los_alumnos[inicio:fin]

    return jsonify(
        {
            "pagina_actual": pagina,
            "cantidad_por_pagina": cantidad,
            "total_alumnos_curso": len(todos_los_alumnos),
            "datos": alumnos_paginados,
        }
    ), 200


@students_bp.route("/api/v1/classrooms/<int:classroom_id>/alumnos", methods=["POST"])
def crear_alumno(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    username = body.get("username")
    email = body.get("email")
    document = body.get("document")
    career = body.get("career")

    if not username or not email or not document or not career:
        return responder_error(DATOS_ESTUDIANTE_REQUERIDOS)

    resultado, error = crear_estudiante_en_classroom(
        classroom_id, usuario["id"], username, email, document, career
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 201
