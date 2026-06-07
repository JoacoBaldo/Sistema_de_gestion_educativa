from .conexion import obtener_conexion
from .constantes import ADMINISTRADOR, AYUDANTE, ESTUDIANTE, PROFESOR, STATUS_ACTIVO, STATUS_ABANDONO


def obtener_promedio_aprobados(classroom_id: int) -> list[dict]:
    """Retorna lista de user_id con sus scores para procesamiento en Python"""
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT g.user_id, g.score
            FROM grades g
            JOIN classroom_users cu
                ON cu.classroom_id = %s
                AND cu.user_id = g.user_id
                AND cu.role_id = %s
            JOIN evaluations e
                ON e.id = g.evaluation_id
                AND e.classroom_id = %s
            """,
            (classroom_id, ESTUDIANTE, classroom_id),
        ).fetchall()
    return [{"user_id": f[0], "score": f[1]} for f in resultados]


def obtener_ingresos_por_año(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT created_at
            FROM classroom_users
            WHERE classroom_id = %s AND role_id = %s
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()
    return [{"created_at": f[0]} for f in resultados]


def obtener_conteos_estudiantes(classroom_id: int) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT status_type_id
            FROM classroom_users
            WHERE classroom_id = %s AND role_id = %s
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()

    status = [f[0] for f in resultados]

    return {
        "total_estudiantes": len(status),
        "total_activos": sum(1 for s in status if s == STATUS_ACTIVO),
        "total_abandonaron": sum(1 for s in status if s == STATUS_ABANDONO),
    }


def obtener_alumnos_aprobados_activos(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email, cu.created_at
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            JOIN grades g
                ON g.user_id = cu.user_id
            JOIN evaluations e
                ON e.id = g.evaluation_id
                AND e.classroom_id = cu.classroom_id
            WHERE cu.classroom_id = %s
              AND cu.role_id = %s
              AND cu.status_type_id = %s
            GROUP BY u.id, u.username, u.email, cu.created_at
            HAVING AVG(g.score) >= 4
            ORDER BY u.username
            """,
            (classroom_id, ESTUDIANTE, STATUS_ACTIVO),
        ).fetchall()
    return [
        {"id": f[0], "username": f[1], "email": f[2], "created_at": f[3]}
        for f in resultados
    ]


def obtener_equipos(classroom_id: int) -> list[dict]:
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
    return [
        {
            "id": f[0],
            "name": f[1],
            "classroom_id": f[2],
            "created_at": f[3],
            "updated_at": f[4],
        }
        for f in resultados
    ]
