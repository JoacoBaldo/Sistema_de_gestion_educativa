from flask import Blueprint, flash, jsonify, redirect, request, session, url_for

from src.funciones.auth import verificar_token
from src.funciones.errores import (
    MIEMBROS_NO_ES_LISTA,
    MIEMBROS_NO_INT,
    NAME_O_MIEMBROS_REQUERIDO,
    NAME_VACIO,
)
from src.funciones.teams import editar_equipo, eliminar_equipo, crear_equipo
from .utils import extraer_token, responder_error

teams_bp = Blueprint("teams", __name__)


def _obtener_token_formulario():
    return (
        request.form.get("token")
        or request.cookies.get("token")
        or session.get("token")
    )


def _redirigir_equipos(classroom_id=None):
    if classroom_id:
        return redirect(
            url_for(
                "classroom_manage",
                classroom_id=classroom_id,
                vista="teams",
            )
        )
    return redirect(request.referrer or url_for("classrooms"))


def _parsear_miembros_formulario():
    miembros = request.form.getlist("miembros")
    return [m.strip() for m in miembros if m and str(m).strip()]


@teams_bp.route("/api/v1/teams/<int:team_id>", methods=["PUT"])
def actualizar_equipo(team_id):
    token = extraer_token()
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


@teams_bp.route("/api/v1/teams/<int:team_id>", methods=["POST"])
def procesar_equipo(team_id):
    token = _obtener_token_formulario()
    if not token:
        flash("Sesión inválida. Vuelve a iniciar sesión.", "error")
        classroom_id = request.form.get("classroom_id")
        return _redirigir_equipos(classroom_id)

    usuario, error = verificar_token(token)
    if error:
        flash(error.get("error", "Sesión inválida"), "error")
        classroom_id = request.form.get("classroom_id")
        return _redirigir_equipos(classroom_id)

    accion = request.form.get("_action", "actualizar")
    classroom_id = request.form.get("classroom_id")

    if accion == "eliminar":
        _, error = eliminar_equipo(int(team_id), usuario["id"])
        if error:
            mensaje = error.get("error") if isinstance(error, dict) else str(error)
            flash(mensaje, "error")
            return _redirigir_equipos(classroom_id)
        flash("Equipo eliminado exitosamente", "success")
        return _redirigir_equipos(classroom_id)

    nombre = request.form.get("nombre_equipo", "").strip()
    miembros = _parsear_miembros_formulario()

    if not nombre:
        flash("El nombre del equipo es requerido", "error")
        return _redirigir_equipos(classroom_id)

    if not miembros:
        flash("Al menos un miembro es requerido", "error")
        return _redirigir_equipos(classroom_id)

    try:
        member_ids = [int(miembro) for miembro in miembros]
    except (TypeError, ValueError):
        flash("Los miembros deben ser estudiantes válidos del aula", "error")
        return _redirigir_equipos(classroom_id)

    _, error = editar_equipo(int(team_id), nombre, member_ids, usuario["id"])
    if error:
        mensaje = error.get("error") if isinstance(error, dict) else str(error)
        flash(mensaje, "error")
        return _redirigir_equipos(classroom_id)

    flash("Equipo actualizado exitosamente", "success")
    return _redirigir_equipos(classroom_id)


@teams_bp.route("/api/v1/teams/<int:team_id>", methods=["DELETE"])
def borrar_equipo(team_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = eliminar_equipo(int(team_id), usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@teams_bp.route("/api/v1/teams", methods=["POST"])
def crear_equipo_formulario():
    token = _obtener_token_formulario()
    if not token:
        flash("Sesión inválida. Vuelve a iniciar sesión.", "error")
        return redirect(url_for("login"))

    usuario, error = verificar_token(token)
    if error:
        flash(error.get("error", "Sesión inválida"), "error")
        return redirect(url_for("login"))

    nombre = request.form.get("nombre_equipo", "").strip()
    miembros = _parsear_miembros_formulario()
    classroom_id_str = request.args.get("classroom_id") or request.form.get(
        "classroom_id"
    )

    try:
        classroom_id = int(classroom_id_str) if classroom_id_str else None
    except (ValueError, TypeError):
        classroom_id = None

    if not nombre:
        flash("El nombre del equipo es requerido", "error")
        return _redirigir_equipos(classroom_id)

    if not miembros:
        flash("Al menos un miembro es requerido", "error")
        return _redirigir_equipos(classroom_id)

    if not classroom_id:
        flash("Classroom no especificado", "error")
        return _redirigir_equipos()

    _, error = crear_equipo(nombre, miembros, classroom_id, usuario["id"])
    if error:
        mensaje = error.get("error") if isinstance(error, dict) else str(error)
        flash(mensaje, "error")
        return _redirigir_equipos(classroom_id)

    flash("Equipo creado exitosamente", "success")
    return _redirigir_equipos(classroom_id)
