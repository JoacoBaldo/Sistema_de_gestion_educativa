from .conexion import obtener_conexion


def crear_evaluacion_db(
    classroom_id: int,
    name: str,
    evaluation_type_id: int,
    referenced_eval_id: int | None,
    individual: int,
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "INSERT INTO evaluations (classroom_id, name, evaluation_type_id, referenced_eval_id, individual) VALUES (%s, %s, %s, %s, %s) RETURNING id",
            (classroom_id, name, evaluation_type_id, referenced_eval_id, individual),
        )
        inserted = resultado.fetchone()
        conn.commit()

    evaluation_id = inserted[0] if inserted else None
    return {
        "message": "Evaluacion creada exitosamente",
        "status": 201,
        "id": evaluation_id,
    }


def existe_evaluation_type(evaluation_type_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM evaluation_types WHERE id = %s LIMIT 1",
            (evaluation_type_id,),
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
