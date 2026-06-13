from datetime import datetime, timezone
from typing import Optional

from .conexion import obtener_conexion


def crear_equipo_con_miembros(
    nombre: str, miembros: list, classroom_id: int
) -> Optional[int]:
    """
    Crea un nuevo equipo y retorna el ID generado por MySQL de forma segura.
    """
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO teams (name, classroom_id, created_at, updated_at)
            VALUES (%s, %s, NOW(), NOW())
            """,
            (nombre, classroom_id),
        )
        conn.commit()
        
        team_id = cursor.lastrowid

        return team_id

def listar_equipos_classroom(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        equipos_raw = conn.exec_driver_sql(
            """
            SELECT t.id, t.name, t.classroom_id, t.created_at, t.updated_at,
            u.id, u.username, u.email
            FROM teams t
            LEFT JOIN team_members tm ON tm.team_id = t.id
            LEFT JOIN users u ON u.id = tm.user_id
            WHERE t.classroom_id = %s
            ORDER BY t.name, u.username
            """,
            (classroom_id,),
        ).fetchall()

    equipos_dict = {}
    for fila in equipos_raw:
        team_id = fila[0]
        if team_id not in equipos_dict:
            equipos_dict[team_id] = {
                "id": team_id,
                "name": fila[1],
                "classroom_id": fila[2],
                "created_at": fila[3],
                "updated_at": fila[4],
                "miembros": [],
            }
        if fila[5]:
            equipos_dict[team_id]["miembros"].append(
                {
                    "id": fila[5],
                    "username": fila[6],
                    "email": fila[7],
                }
            )
    return list(equipos_dict.values())


def obtener_ids_miembros(team_id: int) -> list[int]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        filas = conn.exec_driver_sql(
            "SELECT user_id FROM team_members WHERE team_id = %s",
            (team_id,),
        ).fetchall()
    return [fila[0] for fila in filas]


def obtener_miembros_equipo(team_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email
            FROM team_members tm
            JOIN users u ON u.id = tm.user_id
            WHERE tm.team_id = %s
            ORDER BY u.username
            """,
            (team_id,),
        ).fetchall()

    return [
        {"id": fila[0], "username": fila[1], "email": fila[2]} for fila in resultados
    ]


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


def crear_grades_equipo(evaluation_id: int, team_id: int, member_ids: list[int]):
    engine = obtener_conexion()
    with engine.connect() as conn:
        for user_id in member_ids:
            conn.exec_driver_sql(
                """
                INSERT INTO grades (evaluation_id, user_id, team_id, score, feedback)
                VALUES (%s, %s, %s, NULL, NULL)
                """,
                (evaluation_id, user_id, team_id),
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
