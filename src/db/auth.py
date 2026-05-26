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


def obtener_usuario_por_email(email: str) -> dict | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT id, username, email, role_id, password
            FROM users
            WHERE email = %s
            """,
            (email,),
        ).fetchone()

    if not resultado:
        return None

    return {
        "id": resultado[0],
        "username": resultado[1],
        "email": resultado[2],
        "role_id": resultado[3],
        "password": resultado[4],
    }


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

def buscar_token(token:str):
    engine = obtener_conexion()
    with engine.connect() as conn:
        token_buscado = conn.exec_driver_sql(
            """
            SELECT * FROM sesiones_activas WHERE token = %s LIMIT 1;
            """
        , (token,))
        return token_buscado.fetchone()

def usuario_existe(usuario_id:int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        usuario = conn.exec_driver_sql(
            """
            SELECT id FROM users WHERE id = %s LIMIT 1;
            """
        , (usuario_id,))
        return usuario.fetchone()

def actualizar_contrasenia(usuario_id: int, nueva_contrasenia: str):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE users SET password = %s WHERE id = %s
            """,
            (nueva_contrasenia, usuario_id),
        )
        conn.commit()