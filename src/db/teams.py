from datetime import datetime, timezone
from typing import Optional

from .conexion import obtener_conexion


def obtener_equipo(team_id: int) -> Optional[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        fila = conn.exec_driver_sql(
            """
            SELECT id, name, classroom_id
            FROM teams
            WHERE id = %s
            LIMIT 1
            """,
            (team_id,),
        ).fetchone()

    if fila is None:
        return None

    return {"id": fila[0], "name": fila[1], "classroom_id": fila[2]}


def actualizar_nombre(team_id: int, nombre: str):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE teams
            SET name = %s, updated_at = %s
            WHERE id = %s
            """,
            (nombre, datetime.now(timezone.utc), team_id),
        )
        conn.commit()


def miembros_pertenecen_aula(classroom_id: int, user_ids: list[int]) -> bool:
    if not user_ids:
        return True

    engine = obtener_conexion()
    placeholders = ", ".join(["%s"] * len(user_ids))
    params = (classroom_id, *user_ids)

    with engine.connect() as conn:
        fila = conn.exec_driver_sql(
            f"""
            SELECT COUNT(DISTINCT user_id)
            FROM classroom_users
            WHERE classroom_id = %s AND user_id IN ({placeholders})
            """,
            params,
        ).fetchone()

    return fila[0] == len(user_ids)


def reemplazar_miembros(team_id: int, user_ids: list[int]):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "DELETE FROM team_members WHERE team_id = %s",
            (team_id,),
        )
        for user_id in user_ids:
            conn.exec_driver_sql(
                """
                INSERT INTO team_members (team_id, user_id)
                VALUES (%s, %s)
                """,
                (team_id, user_id),
            )
        conn.commit()


def eliminar_equipo_completo(team_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "DELETE FROM grades WHERE team_id = %s",
            (team_id,),
        )
        conn.exec_driver_sql(
            "DELETE FROM team_members WHERE team_id = %s",
            (team_id,),
        )
        conn.exec_driver_sql(
            "DELETE FROM teams WHERE id = %s",
            (team_id,),
        )
        conn.commit()


def obtener_equipos_db() -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT id, name, classroom_id 
            FROM teams
            """
        ).fetchall()
        
    return [{"id": f[0], "nombre": f[1], "classroom_id": f[2]} for f in resultados]


def crear_equipo_db(nombre: str, id_usuarios: list[int]) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "INSERT INTO teams (name, classroom_id) VALUES (%s, %s) RETURNING id",
            (nombre, 1) 
        )
        nuevo_team_id = resultado.fetchone()[0]
        
        if id_usuarios:
            for user_id in id_usuarios:
                conn.exec_driver_sql(
                    "INSERT INTO team_members (team_id, user_id) VALUES (%s, %s)",
                    (nuevo_team_id, user_id)
                )
        conn.commit()
        
    return {"id": nuevo_team_id, "nombre": nombre, "id_usuarios": id_usuarios}