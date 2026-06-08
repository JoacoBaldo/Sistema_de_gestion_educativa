from datetime import datetime, timezone
from typing import Optional

from .conexion import obtener_conexion


def crear_equipo_con_miembros(
    nombre: str, miembros: list, classroom_id: int
) -> Optional[int]:
    """
    Crea un nuevo equipo con miembros (nombres).
    Retorna el ID del equipo creado o None si falla.
    """
    engine = obtener_conexion()
    with engine.connect() as conn:
        # Insertar el equipo
        conn.exec_driver_sql(
            """
            INSERT INTO teams (name, classroom_id, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
            """,
            (
                nombre,
                classroom_id,
                datetime.now(timezone.utc),
                datetime.now(timezone.utc),
            ),
        )
        conn.commit()

        # Obtener el ID del equipo creado
        fila = conn.exec_driver_sql(
            """
            SELECT id FROM teams WHERE name = %s AND classroom_id = %s
            ORDER BY created_at DESC LIMIT 1
            """,
            (nombre, classroom_id),
        ).fetchone()

        if fila is None:
            return None

        team_id = fila[0]

        # Aquí podrías almacenar los miembros como nombres en un campo JSON
        # o en una tabla separada. Por ahora, dejamos el equipo sin miembros.
        # Los miembros se pueden asociar después según tu estructura de BD.

        return team_id


def listar_equipos_classroom(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT id, name, classroom_id, created_at, updated_at
            FROM teams
            WHERE classroom_id = %s
            ORDER BY name
            """,
            (classroom_id,),
        ).fetchall()

    equipos = []
    for fila in resultados:
        team_id = fila[0]
        miembros = obtener_miembros_equipo(team_id)
        equipos.append(
            {
                "id": team_id,
                "name": fila[1],
                "classroom_id": fila[2],
                "created_at": fila[3],
                "updated_at": fila[4],
                "miembros": miembros,
            }
        )
    return equipos


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
