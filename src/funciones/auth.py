from datetime import datetime, timedelta
from src.db import auth as db_auth
from flask import request
from .errores import TOKEN_INVALIDO, FALTAN_DATOS, USUARIO_NO_EXISTE_GLOBAL

import bcrypt

from src.db import auth as db_auth
from .constantes import TIEMPO_EXPIRACION_HORAS
from .errores import CREDENCIALES_INVALIDAS, TOKEN_INVALIDO


def verificar_token(token: str) -> tuple:
    usuario = db_auth.sesion_existe(token)
    if not usuario:
        return None, TOKEN_INVALIDO
    return usuario, None


def crear_token(usuario_id: int, username: str, email: str) -> str:
    db_auth.eliminar_sesiones_usuario(usuario_id)
    token = db_auth.generar_token()
    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION_HORAS)
    db_auth.guardar_sesion(usuario_id, token, expira_en)
    return token


def datos_completos():
    body = request.get_json()
    token = body.get("token")
    nueva_contraseña = body.get("nueva_contraseña")
    if not token or not nueva_contraseña:
        return token, nueva_contraseña, FALTAN_DATOS
    return token, nueva_contraseña, None


def buscar_token(token: str):
    return db_auth.buscar_token(token), TOKEN_INVALIDO


def usuario_existe(usuario_id: int):
    return db_auth.usuario_existe(usuario_id), USUARIO_NO_EXISTE_GLOBAL


def actualizar_contrasenia(id_usuario: int, hash_generado: str):
    db_auth.actualizar_contrasenia(id_usuario, hash_generado)
    return {"message": "Contraseña actualizada exitosamente"}
