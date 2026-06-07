from flask import Blueprint, jsonify, request, send_file
import io

from scripts.pdf_metricas import generar_pdf_metricas
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


@metrics_bp.route("/api/v1/metrics/<int:classroom_id>/pdf", methods=["POST"])
def descargar_pdf_metricas(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    datos_metricas = request.get_json(silent=True) or {}
    filtro = request.args.get("filter", None)

    pdf_bytes, error = generar_pdf_metricas(
        classroom_id=classroom_id,
        usuario_id=usuario["id"],
        datos_metricas=datos_metricas,
        filtro=filtro,
    )
    if error:
        return responder_error(error)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"metricas_classroom_{classroom_id}.pdf",
    )
