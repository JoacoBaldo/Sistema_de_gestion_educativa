from .conexion import obtener_conexion
from .roles import ADMINISTRADOR, ESTUDIANTE, PROFESOR


def obtener_profesores(classroom_id: int) -> list:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email, cu.role_id
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s AND cu.role_id IN (%s, %s)
            """,
            (classroom_id, PROFESOR, ADMINISTRADOR),
        ).fetchall()

    return [
        {"id": f[0], "username": f[1], "email": f[2], "role_id": f[3]}
        for f in resultados
    ]


def usuario_en_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            LIMIT 1
            """,
            (classroom_id, usuario_id),
        ).fetchone()
    return resultado is not None


def puede_administrar_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s AND role_id IN (%s, %s)
            LIMIT 1
            """,
            (classroom_id, usuario_id, ADMINISTRADOR, PROFESOR),
        ).fetchone()
    return resultado is not None


def eliminar_usuario_classroom(classroom_id: int, usuario_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            """,
            (classroom_id, usuario_id),
        )
        conn.commit()


def obtener_todos_los_periodos() -> list:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT id, name, period_start, period_end
            FROM academic_period
            """
        ).fetchall()

    return [
        {
            "id": f[0],
            "name": f[1],
            "start_date": str(f[2]),
            "end_date": str(f[3]),
        }
        for f in resultados
    ]


def guardar_classroom(name: str, department: str, university: str) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO classrooms (name, department, university)
            VALUES (%s, %s, %s)
            """,
            (name, department, university),
        )
        conn.commit()
        return cursor.lastrowid


def guardar_class_schedule(
    classroom_id: int,
    class_day: int,
    class_start: str,
    class_end: str,
    academic_period_id: int,
) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO class_schedule (classroom_id, class_day, class_start, class_end, academic_period_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (classroom_id, class_day, class_start, class_end, academic_period_id),
        )
        conn.commit()
        return cursor.lastrowid


def asignar_admin_classroom(classroom_id: int, usuario_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO classroom_users (classroom_id, user_id, role_id)
            VALUES (%s, %s, %s)
            """,
            (classroom_id, usuario_id, ADMINISTRADOR),
        )
        conn.commit()


def existe_classroom(classroom_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM classrooms WHERE id = %s LIMIT 1",
            (classroom_id,),
        ).fetchone()
    return resultado is not None


def agregar_usuario_classroom(classroom_id: int, user_id: int, role_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO classroom_users (classroom_id, user_id, role_id)
            VALUES (%s, %s, %s)
            """,
            (classroom_id, user_id, role_id),
        )
        conn.commit()


def obtener_classroom_ids_de_periodos_finalizados() -> list[int]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT DISTINCT cs.classroom_id
            FROM class_schedule cs
            JOIN academic_period ap ON cs.academic_period_id = ap.id
            WHERE ap.period_end < CURDATE()
            """
        ).fetchall()
    return [f[0] for f in resultados]


def desactivar_alumnos_de_classrooms(classroom_ids: list[int]) -> int:
    if not classroom_ids:
        return 0
    placeholders = ", ".join(["%s"] * len(classroom_ids))
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            f"""
            UPDATE classroom_users
            SET status_type_id = 2
            WHERE classroom_id IN ({placeholders})
              AND role_id = %s
              AND status_type_id = 1
            """,
            (*classroom_ids, ESTUDIANTE),
        )
        conn.commit()
        return cursor.rowcount


def obtener_classrooms_usuario(usuario_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = (
            conn.exec_driver_sql(
                """
                SELECT
                    c.id,
                    c.name,
                    c.department,
                    c.university,
                    cs.id AS schedule_id,
                    cs.class_day,
                    cs.class_start,
                    cs.class_end,
                    cs.academic_period_id
                FROM classroom_users cu
                JOIN classrooms c ON cu.classroom_id = c.id
                LEFT JOIN class_schedule cs ON c.id = cs.classroom_id
                WHERE cu.user_id = %s
                """,
                (usuario_id,),
            )
            .mappings()
            .fetchall()
        )

    return [
        {
            "id": fila["id"],
            "name": fila["name"],
            "department": fila["department"],
            "university": fila["university"],
            "schedule": {
                "id": fila["schedule_id"],
                "class_day": fila["class_day"],
                "class_start": str(fila["class_start"])
                if fila["class_start"]
                else None,
                "class_end": str(fila["class_end"]) if fila["class_end"] else None,
                "academic_period_id": fila["academic_period_id"],
            }
            if fila["schedule_id"] is not None
            else None,
        }
        for fila in resultados
    ]

def obtener_alumnos(classroom_id: int) -> list:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email, cu.role_id
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s AND cu.role_id = %s
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()

    return [
        {"id": f[0], "username": f[1], "email": f[2], "role_id": f[3]}
        for f in resultados
    ]
