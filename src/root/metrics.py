from flask import Blueprint, jsonify

from src.funciones.auth import verificar_token
from src.funciones.metrics import obtener_metricas_classroom
from .utils import extraer_token, responder_error

metrics_bp = Blueprint("metrics", __name__)


@metrics_bp.route("/api/v1/metrics/<int:classroom_id>", methods=["GET"])
def metricas_classroom(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_metricas_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
