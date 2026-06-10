from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.classroom import (
    crear_nueva_classroom,
    obtener_link_classroom,
    obtener_lista_classrooms,
    obtener_periodos_academicos,
    datetime_valido
)
from src.funciones.errores import (
    DATOS_INVALIDOS,
    FECHA_INVALIDA,
    ROLE_ID_REQUERIDO,
    SCHEDULE_REQUERIDO,
    USER_ID_NO_COINCIDE,
)

from .utils import extraer_token, responder_error

classroom_bp = Blueprint("classroom", __name__)

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
    class_day = body.get("class_day")
    class_start = body.get("class_start")
    class_end = body.get("class_end")
    academic_period_id = body.get("academic_period_id")

    if not name or not department or not university:
        return responder_error(DATOS_INVALIDOS)

    if class_day is None or not class_start or not class_end or not academic_period_id:
        return responder_error(SCHEDULE_REQUERIDO)

    inicio_clase = datetime_valido(class_start)
    fin_clase = datetime_valido(class_end)
    if inicio_clase is None or fin_clase is None:
        return responder_error(FECHA_INVALIDA)

    if fin_clase <= inicio_clase:
        return responder_error(FECHA_INVALIDA)

    if _contains_full_date(class_end) and fin_clase < datetime.now():
        return responder_error(FECHA_INVALIDA)

    resultado, error = crear_nueva_classroom(
        name,
        department,
        university,
        usuario["id"],
        int(class_day),
        class_start,
        class_end,
        int(academic_period_id),
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), 201
