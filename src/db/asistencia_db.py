from src.db.conexion import obtener_conexion


def crear_evento_asistencia(classroom_id, qr_code, fecha):
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO attendace_events (classroom_id, qr_code, created_at)
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


def inasistencia_db(student_id, attendece_event_id, fecha):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE attendace
            SET student_id = %s, attendece_event_id = %s, absence = absence + 1, updated_at = %s
            """,
            (student_id, attendece_event_id, fecha),
        )
        conn.commit()
        conn.close()

    return {"mensaje": "Inasistencia sumada correctamente", "status_code": 200}
