from .conexion import obtener_conexion


def crear_evaluacion_db(classroom_id: int, fecha: str, aulas: tuple) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "INSERT INTO evaluaciones (classroom_id, fecha, aula) VALUES (%s, %s, %s)",
            (classroom_id, fecha, aulas),
        )
        conn.commit()
    return {"message": "Evaluacion creada exitosamente", "status": 201}


def existe_classroom(classroom_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM classrooms WHERE id = %s LIMIT 1",
            (classroom_id,),
        ).fetchone()
    return resultado is not None
