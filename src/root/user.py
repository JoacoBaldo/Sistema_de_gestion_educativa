from flask import Blueprint, jsonify, request

from src.funciones.errores import DATOS_USUARIO_REQUERIDOS, EMAIL_REQUERIDO
from src.funciones.user import create_user, send_password_mail
from .utils import responder_error

user_bp = Blueprint("user", __name__)


@user_bp.route("/api/v1/create_user", methods=["POST"])
def create_user_route():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return responder_error(DATOS_USUARIO_REQUERIDOS)

    resultado, error = create_user(
        {"username": username, "email": email, "password": password}
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]


@user_bp.route("/recuperar-password", methods=["POST"])
def solicitar_recuperacion():
    data = request.get_json(silent=True) or {}
    email_usuario = data.get("email")

    if not email_usuario:
        return responder_error(EMAIL_REQUERIDO)

    resultado, error = send_password_mail(email_usuario)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@user_bp.route("/api/v1/cargar-csv", methods=["POST"])
def cargar_usuarios_csv():
    if "archivo" not in request.files:
        return jsonify(
            {"error": "No se envió ningún archivo con la clave 'archivo'"}
        ), 400

    archivo = request.files["archivo"]

    if archivo.filename == "":
        return jsonify({"error": "El nombre del archivo está vacío"}), 400

    try:
        contenido_texto = archivo.read().decode("utf-8")
        lineas = contenido_texto.split("\n")
        titulos = lineas[0].strip().split(",")

        usuarios_cargados = []

        for linea in lineas[1:]:
            linea_limpia = linea.strip()
            if not linea_limpia:
                continue

            valores = linea_limpia.split(",")
            usuario = dict(zip(titulos, valores))
            usuarios_cargados.append(usuario)

        usuarios_guardados = 0
        errores_guardado = []

        for u in usuarios_cargados:
            resultado, error = create_user(
                {
                    "username": u.get("username"),
                    "email": u.get("email"),
                    "password": u.get("password"),
                }
            )

            if error:
                errores_guardado.append({"usuario": u.get("email"), "error": error})
            else:
                usuarios_guardados += 1

        return jsonify(
            {
                "status": "ok",
                "mensaje": "Proceso de CSV finalizado",
                "cantidad_procesados": len(usuarios_cargados),
                "cantidad_guardados_ok": usuarios_guardados,
                "errores": errores_guardado,
            }
        ), 200

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500
