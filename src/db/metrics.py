from .conexion import obtener_conexion
from .roles import ESTUDIANTE


def obtener_promedio_aprobados(classroom_id: int) -> float | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT AVG(aprobado) AS promedio_aprobados
            FROM (
                SELECT
                    g.user_id,
                    CASE WHEN AVG(g.score) >= 4 THEN 1 ELSE 0 END AS aprobado
                FROM grades g
                JOIN classroom_users cu
                    ON cu.classroom_id = %s
                    AND cu.user_id = g.user_id
                    AND cu.role_id = %s
                JOIN evaluations e
                    ON e.id = g.evaluation_id
                    AND e.classroom_id = %s
                GROUP BY g.user_id
            ) sub
            """,
            (classroom_id, ESTUDIANTE, classroom_id),
        ).fetchone()
    if resultado is None or resultado[0] is None:
        return None
    return float(resultado[0])


def obtener_ingresos_por_anio(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT YEAR(cu.created_at) AS anio, COUNT(*) AS total
            FROM classroom_users cu
            WHERE cu.classroom_id = %s AND cu.role_id = %s
            GROUP BY YEAR(cu.created_at)
            ORDER BY anio
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()
    return [{"year": int(f[0]), "total": int(f[1])} for f in resultados]


STATUS_ACTIVO = 1
STATUS_ABANDONO = 4


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
