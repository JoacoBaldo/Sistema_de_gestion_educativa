from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.errores import (
    ID_REQUERIDO,
    MIEMBROS_NO_ES_LISTA,
    MIEMBROS_NO_INT,
    NAME_O_MIEMBROS_REQUERIDO,
    NAME_VACIO,
)
from src.funciones.teams import editar_equipo, eliminar_equipo
from .utils import extraer_token, responder_error

teams_bp = Blueprint("teams", __name__)


@teams_bp.route("/api/v1/teams", methods=["PUT"])
def actualizar_equipo():
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    team_id = data.get("id")
    nombre = data.get("name")
    member_ids = data.get("member_ids")

    if team_id is None:
        return responder_error(ID_REQUERIDO)

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


@teams_bp.route("/api/v1/teams", methods=["DELETE"])
def borrar_equipo():
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    data = request.get_json(silent=True) or {}
    team_id = data.get("id")

    if team_id is None:
        return responder_error(ID_REQUERIDO)

    resultado, error = eliminar_equipo(int(team_id), usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
