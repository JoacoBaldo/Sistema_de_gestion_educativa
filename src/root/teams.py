from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.errores import (
    CLASSROOM_NO_ESPECIFICADO,
    MIEMBROS_NO_ES_LISTA,
    MIEMBROS_NO_INT,
    MIEMBROS_REQUERIDO,
    NAME_O_MIEMBROS_REQUERIDO,
    NAME_VACIO,
    SESION_INVALIDA,
)
from src.funciones.teams import crear_equipo, editar_equipo, eliminar_equipo, obtener_equipos_classroom

from .utils import extraer_token, responder_error

teams_bp = Blueprint("teams", __name__)


def _parsear_miembros_formulario():
    miembros = request.form.getlist("miembros")
    return [m.strip() for m in miembros if m and str(m).strip()]


@teams_bp.route("/api/v1/teams", methods=["GET"])
def listar_equipos_api():
    token = extraer_token()
    if not token:
        return responder_error(SESION_INVALIDA)

    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    classroom_id_str = request.args.get("classroom_id")
    if not classroom_id_str:
        return responder_error(CLASSROOM_NO_ESPECIFICADO)

    try:
        classroom_id = int(classroom_id_str)
    except ValueError:
        return responder_error(CLASSROOM_NO_ESPECIFICADO)

    resultado, error = obtener_equipos_classroom(classroom_id, usuario["id"])
    
    if error:
        return responder_error(error)

    return jsonify(resultado), 200

@teams_bp.route("/api/v1/teams/<int:team_id>", methods=["PUT"])
def actualizar_equipo(team_id):
    token = extraer_token()
    if not token:
        return responder_error(SESION_INVALIDA)
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    nombre = data.get("name")
    member_ids = data.get("member_ids")

    if nombre is None and member_ids is None:
        return responder_error(NAME_O_MIEMBROS_REQUERIDO)

    if nombre is not None and not str(nombre).strip():
        return responder_error(NAME_VACIO)

    if member_ids is not None:
        if not isinstance(member_ids, list):
            return responder_error(MIEMBROS_NO_ES_LISTA)
        try:
            member_ids = [int(uid) for uid in member_ids]
        except (TypeError, ValueError):
            return responder_error(MIEMBROS_NO_INT)

    resultado, error = editar_equipo(int(team_id), nombre, member_ids, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@teams_bp.route("/api/v1/teams/<int:team_id>", methods=["DELETE"])
def borrar_equipo(team_id):
    token = extraer_token()
    if not token:
        return responder_error(SESION_INVALIDA)
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_equipo(int(team_id), usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@teams_bp.route("/api/v1/teams", methods=["POST"])
def crear_equipo_formulario():
    token = extraer_token()
    if not token:
        return responder_error(SESION_INVALIDA)

    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    nombre = data.get("name", "").strip()
    miembros = data.get("member_ids", [])
    classroom_id = data.get("classroom_id")

    if not nombre:
        return responder_error(NAME_VACIO)

    if not miembros:
        return responder_error(MIEMBROS_REQUERIDO)

    if not classroom_id:
        return responder_error(CLASSROOM_NO_ESPECIFICADO) [cite: 30]

    resultado, error = crear_equipo(nombre, miembros, int(classroom_id), usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 201
