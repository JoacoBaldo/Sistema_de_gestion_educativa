from datetime import datetime, timezone
from typing import Optional

from .conexion import cursor_db


def obtener_equipo(team_id: int) -> Optional[dict]:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT id, name, classroom_id
            FROM teams
            WHERE id = %s
            LIMIT 1
            """,
            (team_id,),
        )
        fila = cur.fetchone()

    if fila is None:
        return None

    return {"id": fila["id"], "name": fila["name"], "classroom_id": fila["classroom_id"]}


def actualizar_nombre(team_id: int, nombre: str):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            UPDATE teams
            SET name = %s, updated_at = %s
            WHERE id = %s
            """,
            (nombre, datetime.now(timezone.utc), team_id),
        )


def miembros_pertenecen_aula(classroom_id: int, user_ids: list[int]) -> bool:
    if not user_ids:
        return True

    placeholders = ", ".join(["%s"] * len(user_ids))
    params = (classroom_id, *user_ids)

    with cursor_db() as cur:
        cur.execute(
            f"""
            SELECT COUNT(DISTINCT user_id) AS total
            FROM classroom_users
            WHERE classroom_id = %s AND user_id IN ({placeholders})
            """,
            params,
        )
        fila = cur.fetchone()

    return fila["total"] == len(user_ids)


def reemplazar_miembros(team_id: int, user_ids: list[int]):
    with cursor_db(commit=True) as cur:
        cur.execute(
            "DELETE FROM team_members WHERE team_id = %s",
            (team_id,),
        )
        for user_id in user_ids:
            cur.execute(
                """
                INSERT INTO team_members (team_id, user_id)
                VALUES (%s, %s)
                """,
                (team_id, user_id),
            )


def eliminar_equipo_completo(team_id: int):
    with cursor_db(commit=True) as cur:
        cur.execute(
            "DELETE FROM grades WHERE team_id = %s",
            (team_id,),
        )
        cur.execute(
            "DELETE FROM team_members WHERE team_id = %s",
            (team_id,),
        )
        cur.execute(
            "DELETE FROM teams WHERE id = %s",
            (team_id,),
        )
