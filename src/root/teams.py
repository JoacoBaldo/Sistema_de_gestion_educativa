from flask import Blueprint, jsonify, request, redirect, url_for, session

from src.funciones.auth import verificar_token
from src.funciones.errores import (
    ID_REQUERIDO,
    MIEMBROS_NO_ES_LISTA,
    MIEMBROS_NO_INT,
    NAME_O_MIEMBROS_REQUERIDO,
    NAME_VACIO,
)
from src.funciones.teams import editar_equipo, eliminar_equipo, crear_equipo
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


# === NUEVAS RUTAS PARA FORMULARIOS HTML TRADICIONALES ===


@teams_bp.route("/equipos/<int:team_id>/actualizar", methods=["POST"])
def actualizar_equipo_formulario(team_id):
    """
    Ruta para actualizar equipo via formulario HTML tradicional.
    Lee datos de request.form y redirige tras procesamiento.
    """
    token = request.form.get("token") or request.cookies.get("token")
    if not token:
        return redirect(url_for("error_page") or "/")
    
    usuario, error = verificar_token(token)
    if error:
        return redirect(url_for("error_page") or "/")

    nombre = request.form.get("nombre_equipo", "").strip()
    miembros = request.form.getlist("miembros")
    miembros = [m.strip() for m in miembros if m.strip()]

    if not nombre:
        session["error"] = "El nombre del equipo es requerido"
        return redirect(request.referrer or "/")

    if not miembros:
        session["error"] = "Al menos un miembro es requerido"
        return redirect(request.referrer or "/")

    resultado, error = editar_equipo(int(team_id), nombre, None, usuario["id"])
    if error:
        session["error"] = str(error)
        return redirect(request.referrer or "/")

    session["success"] = "Equipo actualizado exitosamente"
    return redirect(request.referrer or "/")


@teams_bp.route("/equipos/<int:team_id>/eliminar", methods=["POST"])
def eliminar_equipo_formulario(team_id):
    """
    Ruta para eliminar equipo via formulario HTML tradicional.
    Lee token de formulario y redirige tras procesamiento.
    """
    token = request.form.get("token") or request.cookies.get("token")
    if not token:
        return redirect(url_for("error_page") or "/")
    
    usuario, error = verificar_token(token)
    if error:
        return redirect(url_for("error_page") or "/")

    resultado, error = eliminar_equipo(int(team_id), usuario["id"])
    if error:
        session["error"] = str(error)
        return redirect(request.referrer or "/")

    session["success"] = "Equipo eliminado exitosamente"
    return redirect(request.referrer or "/")


@teams_bp.route("/equipos", methods=["POST"])
def crear_equipo_formulario():
    """
    Ruta para crear equipo via formulario HTML tradicional.
    Lee datos de request.form y redirige tras procesamiento.
    """
    token = request.form.get("token") or request.cookies.get("token")
    if not token:
        return redirect(url_for("error_page") or "/")
    
    usuario, error = verificar_token(token)
    if error:
        return redirect(url_for("error_page") or "/")

    nombre = request.form.get("nombre_equipo", "").strip()
    miembros = request.form.getlist("miembros")
    miembros = [m.strip() for m in miembros if m.strip()]
    
    # Obtener classroom_id de la query string o del formulario
    classroom_id_str = request.args.get("classroom_id") or request.form.get("classroom_id")
    
    try:
        classroom_id = int(classroom_id_str) if classroom_id_str else None
    except (ValueError, TypeError):
        classroom_id = None

    if not nombre:
        session["error"] = "El nombre del equipo es requerido"
        return redirect(request.referrer or "/")

    if not miembros:
        session["error"] = "Al menos un miembro es requerido"
        return redirect(request.referrer or "/")

    if not classroom_id:
        session["error"] = "Classroom no especificado"
        return redirect(request.referrer or "/")

    resultado, error = crear_equipo(nombre, miembros, classroom_id, usuario["id"])
    if error:
        session["error"] = str(error)
        return redirect(request.referrer or "/")

    session["success"] = "Equipo creado exitosamente"
    return redirect(request.referrer or "/")
