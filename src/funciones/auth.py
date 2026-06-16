from datetime import datetime, timedelta
from src.db import auth as db_auth
from flask import request
import bcrypt

from src.db import classroom as db_classroom

from .constantes import TIEMPO_EXPIRACION_HORAS
from .errores import (
    FALTAN_DATOS,
    CREDENCIALES_INVALIDAS,
    LINK_INVALIDO,
    TOKEN_INVALIDO,
    USUARIO_YA_EN_CLASSROOM,
)


def verificar_token(token: str) -> tuple:
    usuario = db_auth.sesion_existe(token)
    if not usuario:
        return None, TOKEN_INVALIDO
    return usuario, None


def crear_token(usuario: dict) -> str:
    db_auth.eliminar_sesiones_usuario(usuario["id"])
    token = db_auth.generar_token()
    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION_HORAS)
    db_auth.guardar_sesion(usuario["id"], token, expira_en)
    return token


def login_con_link(email: str, password: str, join_token: str) -> tuple:
    usuario, error = validar_credenciales(email, password)
    if error:
        return None, error

    link = db_auth.obtener_link_join(join_token)
    if not link:
        return None, LINK_INVALIDO

    classroom_id = link["classroom_id"]
    role_id = link["role_id"]

    if db_classroom.usuario_en_classroom(classroom_id, usuario["id"]):
        return None, USUARIO_YA_EN_CLASSROOM

    db_classroom.agregar_usuario_classroom(classroom_id, usuario["id"], role_id)

    token = crear_token(usuario)
    return {**usuario, "role_id": role_id, "token": token}, None


def buscar_token(token: str):
    token_activo = db_auth.buscar_token(token)
    return token_activo, None if token_activo else TOKEN_INVALIDO


def actualizar_contrasenia(id_usuario: int, hash_generado: str):
    db_auth.actualizar_contrasenia(id_usuario, hash_generado)
    return {"message": "Contraseña actualizada exitosamente"}


def validar_credenciales(email: str, password: str) -> tuple:
    usuario = db_auth.obtener_usuario_por_email(email)
    if not usuario:
        return None, CREDENCIALES_INVALIDAS

    if not bcrypt.checkpw(
        password.encode("utf-8"), usuario["password"].encode("utf-8")
    ):
        return None, CREDENCIALES_INVALIDAS
    return {
        "id": usuario["id"],
        "username": usuario["username"],
        "email": usuario["email"],
    }, None


def datos_completos():
    body = request.get_json()
    token = body.get("token")
    nueva_contraseña = body.get("nueva_contraseña")
    if not token or not nueva_contraseña:
        return token, nueva_contraseña, FALTAN_DATOS
    return token, nueva_contraseña, None


def usuario_existe(usuario_id: int):
    usuario = db_auth.usuario_existe(usuario_id)
    return usuario, None if usuario else USUARIO_NO_EXISTE_GLOBAL
