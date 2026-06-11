from .conexion import obtener_conexion
from .constantes import ESTUDIANTE


def contar_eventos_classroom(classroom_id: int) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT COUNT(*) FROM attendance_events
            WHERE classroom_id = %s
            """,
            (classroom_id,),
        ).fetchone()
    return resultado[0] if resultado else 0


def obtener_inasistencias_por_alumno(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT
                u.id AS student_id,
                u.username AS username,
                u.email AS email,
                COALESCE(SUM(a.absence), 0) AS inasistencias
            FROM classroom_users cu
            JOIN users u ON u.id = cu.user_id
            LEFT JOIN attendance_events ae
                ON ae.classroom_id = cu.classroom_id
            LEFT JOIN attendance a
                ON a.student_id = cu.user_id
                AND a.attendance_event_id = ae.id
            WHERE cu.classroom_id = %s
                AND cu.role_id = %s
            GROUP BY u.id, u.username, u.email
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()
    return [
        {
            "student_id": f[0],
            "username": f[1],
            "email": f[2],
            "inasistencias": int(f[3] or 0),
        }
        for f in resultados
    ]


def crear_evento_asistencia(classroom_id, qr_code, fecha):
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO attendance_events (classroom_id, qr_code, created_at)
            VALUES (%s, %s, %s)
            """,
            (classroom_id, qr_code, fecha),
        )
        conn.commit()
        return cursor.lastrowid


def obtener_estudiantes_classroom(classroom_id):
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT user_id FROM classroom_users WHERE classroom_id = %s AND role_id = 3
            """,
            (classroom_id,),
        ).fetchall()
    resultados_devolver = []
    for fila in resultados:
        resultados_devolver.append(fila[0])
    return resultados_devolver


def inasistencia_db(student_id, attendance_event_id, fecha, delta: int = 1):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE attendance
            SET student_id = %s, attendance_event_id = %s, absence = GREATEST(0, absence + %s), updated_at = %s
            """,
            (student_id, attendance_event_id, delta, fecha),
        )
        conn.commit()
        conn.close()

    return {"mensaje": "Inasistencia actualizada correctamente", "status_code": 200}
