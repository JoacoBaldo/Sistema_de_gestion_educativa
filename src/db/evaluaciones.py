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


def eliminar_evaluacion_db(eval_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "DELETE FROM evaluaciones WHERE id = %s",
            (eval_id,)
        )
        conn.commit()


def insertar_notas_csv_db(eval_id: int, lista_notas: list[dict]) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        for nota_data in lista_notas:
            conn.exec_driver_sql(
                """
                INSERT INTO grades (evaluacion_id, student_id, grade) 
                VALUES (%s, %s, %s)
                """,
                (eval_id, nota_data["padron"], nota_data["nota"])
            )
        conn.commit()
        
    return len(lista_notas)