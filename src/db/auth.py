import secrets
from datetime import datetime, timedelta
from sqlalchemy import text
from .conexion import obtener_conexion

def generar_token():
    return secrets.token_hex(16)

def guardar_sesion(usuario_id: int, token: str, expira_en: datetime):
    engine = obtener_conexion()
    query = text("""
        INSERT INTO sesiones_activas (usuario_id, token, expira_en)
        VALUES (:usuario_id, :token, :expira_en)
    """)
    with engine.connect() as conn:
        conn.execute(query, {
            "usuario_id": usuario_id,
            "token": token,
            "expira_en": expira_en
        })
        conn.commit()

def obtener_usuario_de_token(token: str) -> dict:
    engine = obtener_conexion()
    query = text("""
        SELECT u.id, u.username, u.email
        FROM sesiones_activas s
        JOIN users u ON s.usuario_id = u.id
        WHERE s.token = :token AND s.expira_en > NOW()
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {"token": token}).fetchone()

    if not resultado:
        return None

    return {
        "id": resultado[0],
        "username": resultado[1],
        "email": resultado[2]
    }

def eliminar_sesion(token: str):
    engine = obtener_conexion()
    query = text("""
        DELETE FROM sesiones_activas WHERE token = :token
    """)
    with engine.connect() as conn:
        conn.execute(query, {"token": token})
        conn.commit()
