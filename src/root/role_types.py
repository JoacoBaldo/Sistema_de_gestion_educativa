from flask import Blueprint, jsonify

from src.funciones.auth import verificar_token
from src.funciones.role_types import listar_role_types
from .utils import extraer_token, responder_error

role_types_bp = Blueprint("role_types", __name__)


@role_types_bp.route("/api/v1/role_types", methods=["GET"])
def listar_roles():
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = listar_role_types()
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
