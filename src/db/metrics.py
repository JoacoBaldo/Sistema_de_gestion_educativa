from .conexion import obtener_conexion
from .constantes import ESTUDIANTE, STATUS_ACTIVO, STATUS_ABANDONO


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
