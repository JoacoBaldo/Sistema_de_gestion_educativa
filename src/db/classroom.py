from .conexion import cursor_db
from .roles import ADMINISTRADOR, PROFESOR


def obtener_profesores(classroom_id: int) -> list:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT u.id, u.username, u.email, cu.role_id
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s AND cu.role_id IN (%s, %s)
            """,
            (classroom_id, PROFESOR, ADMINISTRADOR),
        )
        resultados = cur.fetchall()

    return [
        {
            "id": fila["id"],
            "username": fila["username"],
            "email": fila["email"],
            "role_id": fila["role_id"],
        }
        for fila in resultados
    ]


def usuario_en_classroom(classroom_id: int, usuario_id: int) -> bool:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            LIMIT 1
            """,
            (classroom_id, usuario_id),
        )
        return cur.fetchone() is not None


def puede_administrar_classroom(classroom_id: int, usuario_id: int) -> bool:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s AND role_id IN (%s, %s)
            LIMIT 1
            """,
            (classroom_id, usuario_id, ADMINISTRADOR, PROFESOR),
        )
        return cur.fetchone() is not None


def eliminar_usuario_classroom(classroom_id: int, usuario_id: int):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            DELETE FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            """,
            (classroom_id, usuario_id),
        )


def obtener_todos_los_periodos() -> list:
    with cursor_db() as cur:
        cur.execute(
            """
            SELECT id, name, period_start, period_end
            FROM academic_period
            """
        )
        resultados = cur.fetchall()

    return [
        {
            "id": fila["id"],
            "name": fila["name"],
            "start_date": str(fila["start_date"]),
            "end_date": str(fila["end_date"]),
        }
        for fila in resultados
    ]


def guardar_classroom(name: str, department: str, university: str) -> int:
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO classrooms (name, department, university)
            VALUES (%s, %s, %s)
            """,
            (name, department, university),
        )
        return cur.lastrowid


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
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO classroom_users (classroom_id, user_id, role_id)
            VALUES (%s, %s, %s)
            """,
            (classroom_id, usuario_id, ADMINISTRADOR),
        )


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
        resultados = cur.fetchall()

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
