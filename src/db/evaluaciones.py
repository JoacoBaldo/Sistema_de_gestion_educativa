from .conexion import obtener_conexion


def crear_evaluacion_db(classroom_id, fecha, aulas):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "INSERT INTO evaluaciones (classroom_id, fecha, aula) VALUES (%s, %s, %s)",
            (classroom_id, fecha, aulas),
        )
        conn.commit()
        return {"message": "Evaluacion creada exitosamente", "status_code": 201}


def existe_classroom(classroom_id):
    engine = obtener_conexion()
    with engine.connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT 1 FROM classrooms WHERE id = %s LIMIT 1"
            cursor.execute(sql, (classroom_id,))
            result = cursor.fetchone()
        return result is True


