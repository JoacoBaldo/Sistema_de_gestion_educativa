from flask import Blueprint, jsonify, request
from src.funciones.errores import (
    DATOS_USUARIO_REQUERIDOS,
    EMAIL_REQUERIDO,
    LINK_INVALIDO,
    PASSWORD_REQUERIDO,
    FALTAN_DATOS,
    TOKEN_INVALIDO,
    USUARIO_NO_EXISTE,
)
from werkzeug.security import generate_password_hash
from src.funciones.auth import (
    datos_completos,
    buscar_token,
    actualizar_contrasenia as actualizar_contrasenia_func,
    crear_token,
    login_con_link,
    validar_credenciales,
)
from src.funciones.user import usuario_existe, create_user, send_password_mail

from .utils import responder_error

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/v1/login/join", methods=["POST"])
def login_join():
    join_token = request.args.get("token")
    if not join_token:
        return responder_error(LINK_INVALIDO)

    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email:
        return responder_error(EMAIL_REQUERIDO)

    if not password:
        return responder_error(PASSWORD_REQUERIDO)

    resultado, error = login_con_link(email, password, join_token)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200


@auth_bp.route("/api/v1/users/login", methods=["POST"])
def login():
    body = request.get_json(silent=True) or {}
    email = body.get("email")
    password = body.get("password")

    if not email:
        return responder_error(EMAIL_REQUERIDO)

    if not password:
        return responder_error(PASSWORD_REQUERIDO)

    usuario, error = validar_credenciales(email, password)

    if error:
        return responder_error(error)

    token = crear_token(usuario)

    return (
        jsonify(
            {
                "id": usuario["id"],
                "username": usuario["username"],
                "email": usuario["email"],
                "token": token,
            }
        ),
        200,
    )


@auth_bp.route("/api/auth/password", methods=["POST"])
def actualizar_contrasenia_route():

    token, nueva_contrasenia, error = datos_completos()

    if error:
        return responder_error(FALTAN_DATOS)

    token_activo, error = buscar_token(token)

    if error:
        return responder_error(TOKEN_INVALIDO)

    id_usuario, error = usuario_existe(token_activo.usuario_id)

    if error:
        return responder_error(USUARIO_NO_EXISTE)

    hash_generado = generate_password_hash(nueva_contrasenia)

    resultado = actualizar_contrasenia_func(id_usuario, hash_generado)
    
    return jsonify(resultado), 200

@auth_bp.route("/api/v1/register", methods=["POST"])
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


@auth_bp.route("/recuperar-password", methods=["POST"])
def solicitar_recuperacion():
    data = request.get_json(silent=True) or {}
    email_usuario = data.get("email")

    if not email_usuario:
        return responder_error(EMAIL_REQUERIDO)

    resultado, error = send_password_mail(email_usuario)
    if error:
        return responder_error(error)

    return jsonify(resultado), 200
