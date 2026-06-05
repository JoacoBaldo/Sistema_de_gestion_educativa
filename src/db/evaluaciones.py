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
        conn.exec_driver_sql(
            "INSERT INTO evaluations (classroom_id, name, evaluation_type_id, referenced_eval_id, individual) VALUES (%s, %s, %s, %s, %s)",
            (classroom_id, name, evaluation_type_id, referenced_eval_id, individual),
        )
        conn.commit()
    return {"message": "Evaluacion creada exitosamente", "status": 201}


def existe_evaluation_type(evaluation_type_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM evaluation_types WHERE id = %s LIMIT 1",
            (evaluation_type_id,),
        ).fetchone()
    return resultado is not None


def existe_evaluacion_en_classroom(evaluation_id: int, classroom_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM evaluations WHERE id = %s AND classroom_id = %s LIMIT 1",
            (evaluation_id, classroom_id),
        ).fetchone()
    return resultado is not None
