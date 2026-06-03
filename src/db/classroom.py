from .conexion import obtener_conexion
from .roles import ADMINISTRADOR, PROFESOR


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
            SELECT id, name, start_date, end_date
            FROM academic_periods
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
                    c.schedule_id,
                    c.class_day,
                    c.class_start,
                    c.class_end,
                    ap.id AS ap_id,
                    ap.name AS ap_name,
                    ap.period_start AS ap_start,
                    ap.period_end AS ap_end
                FROM classroom_users cu
                JOIN classrooms c ON cu.classroom_id = c.id
                LEFT JOIN academic_periods ap ON c.id = ap.classroom_id
                WHERE cu.user_id = %s
                """,
                (usuario_id,),
            )
            .mappings()
            .fetchall()
        )

    classrooms_dict = {}
    for fila in resultados:
        class_id = fila["id"]
        if class_id not in classrooms_dict:
            classrooms_dict[class_id] = {
                "id": class_id,
                "name": fila["name"],
                "department": fila["department"],
                "university": fila["university"],
                "schedule_id": fila["schedule_id"],
                "class_day": fila["class_day"],
                "class_start": str(fila["class_start"])
                if fila["class_start"]
                else None,
                "class_end": str(fila["class_end"]) if fila["class_end"] else None,
                "academic_periods": [],
            }
        if fila["ap_id"] is not None:
            classrooms_dict[class_id]["academic_periods"].append(
                {
                    "id": fila["ap_id"],
                    "name": fila["ap_name"],
                    "period_start": str(fila["ap_start"])
                    if fila["ap_start"] is not None
                    else None,
                    "period_end": str(fila["ap_end"])
                    if fila["ap_end"] is not None
                    else None,
                }
            )

    return list(classrooms_dict.values())
