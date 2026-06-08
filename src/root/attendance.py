from flask import Blueprint, jsonify, render_template, request

from src.funciones.attendance import obtener_inasistencias_classroom, obtener_datos_qr, procesar_registro_presente
from src.funciones.auth import verificar_token
from .utils import extraer_token, responder_error

attendance_bp = Blueprint("attendance", __name__)


@attendance_bp.route("/api/v1/attendance/<int:classroom_id>", methods=["GET"])
def listar_inasistencias(classroom_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error = obtener_inasistencias_classroom(classroom_id, usuario["id"])
    if error:
        return responder_error(error)

    return jsonify(resultado), 200

@attendance_bp.route("/asistencia/qr/<token>", methods=["GET"])
def mostrar_asistencia(token):
    clase_data, error = obtener_datos_qr(token)
    
    if error:
        return render_template("asistencia_error.html", mensaje=error["error"])
    
    padron_usuario = ""
    
    return render_template(
        "asistencia_alumno.html", 
        token=token, 
        clase=clase_data, 
        padron=padron_usuario
    )

@attendance_bp.route("/api/v1/asistencia/registrar", methods=["POST"])
def registrar_presente_root():
    data = request.get_json(silent=True) or {}
    token = data.get("token")
    padron = str(data.get("padron", "")).strip()
    
    resultado, error = procesar_registro_presente(token, padron)
    
    if error:
        return jsonify(error), error["status"]
        
    return jsonify(resultado), 200