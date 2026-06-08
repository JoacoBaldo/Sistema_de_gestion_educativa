from flask import Blueprint, jsonify, request

from src.funciones.auth import verificar_token
from src.funciones.errores import ARCHIVO_NO_ENVIADO, ARCHIVO_VACIO
from src.funciones.students import cargar_estudiantes_csv
from .utils import extraer_token, responder_error

students_bp = Blueprint("students", __name__)


@students_bp.route("/api/v1/cargar-csv", methods=["POST"])
def cargar_usuarios_csv():
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    if "archivo" not in request.files:
        return responder_error(ARCHIVO_NO_ENVIADO)

    archivo = request.files["archivo"]
    if archivo.filename == "":
        return responder_error(ARCHIVO_VACIO)

    resultado, error = cargar_estudiantes_csv(archivo)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
