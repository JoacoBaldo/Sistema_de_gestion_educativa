from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.teams import editar_equipo, eliminar_equipo

teams_bp = Blueprint("teams", __name__)


def _extraer_token():
    return request.headers.get("Authorization", "").removeprefix("Bearer ").strip()


@teams_bp.route("/api/v1/teams", methods=["PUT"])
def actualizar_equipo():
    token = _extraer_token()
    usuario, error = verificar_token(token)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    data = request.get_json(silent=True) or {}
    team_id = data.get("id")
    nombre = data.get("name")
    member_ids = data.get("member_ids")

    if team_id is None:
        return jsonify({"error": "id es requerido"}), 400

    if nombre is None and member_ids is None:
        return jsonify({"error": "Se requiere name o member_ids"}), 400

    if nombre is not None and not str(nombre).strip():
        return jsonify({"error": "name no puede estar vacío"}), 400

    if member_ids is not None:
        if not isinstance(member_ids, list):
            return jsonify({"error": "member_ids debe ser una lista"}), 400
        try:
            member_ids = [int(uid) for uid in member_ids]
        except (TypeError, ValueError):
            return jsonify({"error": "member_ids debe contener enteros"}), 400

    resultado, error = editar_equipo(
        int(team_id),
        nombre,
        member_ids,
        usuario["id"],
    )

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200


@teams_bp.route("/api/v1/teams", methods=["DELETE"])
def borrar_equipo():
    token = _extraer_token()
    usuario, error = verificar_token(token)

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    data = request.get_json(silent=True) or {}
    team_id = data.get("id")

    if team_id is None:
        return jsonify({"error": "id es requerido"}), 400

    resultado, error = eliminar_equipo(int(team_id), usuario["id"])

    if error:
        return jsonify({"error": error["error"]}), error["status"]

    return jsonify(resultado), 200
