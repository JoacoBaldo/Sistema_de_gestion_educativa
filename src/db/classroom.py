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
            SELECT id, name, start_date, end_date
            FROM academic_periods
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


def asignar_admin_classroom(classroom_id: int, usuario_id: int):
    with cursor_db(commit=True) as cur:
        cur.execute(
            """
            INSERT INTO classroom_users (classroom_id, user_id, role_id)
            VALUES (%s, %s, %s)
            """,
            (classroom_id, usuario_id, ADMINISTRADOR),
        )


def obtener_classrooms_usuario(usuario_id: int) -> list[dict]:
    with cursor_db() as cur:
        cur.execute(
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
        resultados = cur.fetchall()

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
