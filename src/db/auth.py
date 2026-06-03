import secrets
from datetime import datetime

from .conexion import cursor_db


def generar_token():
    return secrets.token_hex(16)


def guardar_sesion(usuario_id: int, token: str, expira_en: datetime):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO sesiones_activas (usuario_id, token, expira_en)
            VALUES (%s, %s, %s)
            """,
            (usuario_id, token, expira_en),
        )


def sesion_existe(token: str) -> dict | None:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email
            FROM sesiones_activas s
            JOIN users u ON s.usuario_id = u.id
            WHERE s.token = %s AND s.expira_en > NOW()
            """,
            (token,),
        )
        resultado = cur.fetchone()

    if not resultado:
        return None

    return {
        "id": resultado["id"],
        "username": resultado["username"],
        "email": resultado["email"],
    }


def obtener_usuario_por_email(email: str) -> dict | None:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT id, username, email, password
            FROM users
            WHERE email = %s
            """,
            (email,),
        )
        resultado = cur.fetchone()

    if not resultado:
        return None

    return {
        "id": resultado[0],
        "username": resultado[1],
        "email": resultado[2],
        "password": resultado[3],
    }


def generar_link_classroom(classroom_id: int, role_id: int, expira_en: datetime) -> str:
    token = generar_token()
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO sesiones_activas (classroom_id, role_id, token, expira_en)
            VALUES (%s, %s, %s, %s)
            """,
            (classroom_id, role_id, token, expira_en),
        )
    return token


def eliminar_sesiones_usuario(usuario_id: int):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            DELETE FROM sesiones_activas WHERE usuario_id = %s
            """,
            (usuario_id,),
        )


def buscar_token(token: str):
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT * FROM sesiones_activas WHERE token = %s LIMIT 1
            """,
            (token,),
        )
        return cur.fetchone()


def usuario_existe(usuario_id: int):
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT id FROM users WHERE id = %s LIMIT 1
            """,
            (usuario_id,),
        )
        return cur.fetchone()


def actualizar_contrasenia(usuario_id: int, nueva_contrasenia: str):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            UPDATE users SET password = %s WHERE id = %s
            """,
            (nueva_contrasenia, usuario_id),
        )
