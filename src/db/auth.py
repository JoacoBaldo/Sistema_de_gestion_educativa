import secrets
from datetime import datetime
from .conexion import obtener_conexion


def generar_token():
    return secrets.token_hex(16)


def guardar_sesion(usuario_id: int, token: str, expira_en: datetime):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO sesiones_activas (usuario_id, token, expira_en)
            VALUES (%s, %s, %s)
            """,
            (usuario_id, token, expira_en),
        )
        conn.commit()


def sesion_existe(token: str) -> dict | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email
            FROM sesiones_activas s
            JOIN users u ON s.usuario_id = u.id
            WHERE s.token = %s AND s.expira_en > NOW()
            """,
            (token,),
        ).fetchone()

    if not resultado:
        return None

    return {"id": resultado[0], "username": resultado[1], "email": resultado[2]}


def generar_link_classroom(classroom_id: int, role_id: int, expira_en: datetime) -> str:
    token = generar_token()
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO sesiones_activas (classroom_id, role_id, token, expira_en)
            VALUES (%s, %s, %s, %s)
            """,
            (classroom_id, role_id, token, expira_en),
        )
        conn.commit()
    return token


def eliminar_sesiones_usuario(usuario_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM sesiones_activas WHERE usuario_id = %s
            """,
            (usuario_id,),
        )
        conn.commit()
