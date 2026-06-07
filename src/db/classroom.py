from .conexion import obtener_conexion
from .constantes import ADMINISTRADOR, ESTUDIANTE, PROFESOR, AYUDANTE


def obtener_profesores(classroom_id: int) -> list:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email, cu.role_id, cu.created_at
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s AND cu.role_id IN (%s, %s, %s)
            ORDER BY cu.role_id, u.username
            """,
            (classroom_id, PROFESOR, AYUDANTE, ADMINISTRADOR),
        ).fetchall()

    return [
        {
            "id": f[0],
            "username": f[1],
            "email": f[2],
            "role_id": f[3],
            "created_at": f[4],
        }
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


def normalizar_horario_a_datetime(valor: str) -> str:
    """Convierte HH:MM o HH:MM:SS al formato datetime que exige MySQL."""
    if not valor:
        return valor

    texto = str(valor).strip().replace("T", " ")
    if " " in texto:
        partes = texto.split(" ", 1)
        fecha, hora = partes[0], partes[1]
        if len(hora) == 5:
            hora = f"{hora}:00"
        return f"{fecha} {hora}"

    if len(texto) == 5:
        return f"1970-01-01 {texto}:00"
    if len(texto) == 8:
        return f"1970-01-01 {texto}"

    return texto


def formatear_hora_desde_db(valor) -> str | None:
    if valor is None:
        return None

    texto = str(valor).strip()
    if " " in texto:
        hora = texto.split(" ", 1)[1]
        return hora[:5] if len(hora) >= 5 else hora

    return texto[:5] if len(texto) >= 5 else texto


def guardar_class_schedule(
    classroom_id: int,
    class_day: int,
    class_start: str,
    class_end: str,
    academic_period_id: int,
) -> int:
    inicio = normalizar_horario_a_datetime(class_start)
    fin = normalizar_horario_a_datetime(class_end)

    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO class_schedule (classroom_id, class_day, class_start, class_end, academic_period_id)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (classroom_id, class_day, inicio, fin, academic_period_id),
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
                "class_start": formatear_hora_desde_db(fila["class_start"]),
                "class_end": formatear_hora_desde_db(fila["class_end"]),
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
            SELECT u.id, u.username, u.email, cu.status_type_id, cu.created_at
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s AND cu.role_id = %s
            ORDER BY u.username
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()

    return [
        {
            "id": f[0],
            "username": f[1],
            "email": f[2],
            "status_type_id": f[3],
            "created_at": f[4],
        }
        for f in resultados
    ]
