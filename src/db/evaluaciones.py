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
        inserted = result.fetchone()
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


def existe_evaluacion_en_classroom(evaluation_id: int, classroom_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM evaluations WHERE id = %s AND classroom_id = %s LIMIT 1",
            (evaluation_id, classroom_id),
        ).fetchone()
    return resultado is not None


def obtener_evaluacion_por_id(evaluation_id: int) -> dict | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT id, classroom_id, name, evaluation_type_id, referenced_eval_id, individual FROM evaluations WHERE id = %s LIMIT 1",
            (evaluation_id,),
        ).mappings().fetchone()
    return dict(resultado) if resultado else None


def actualizar_evaluacion_db(
    classroom_id: int | None,
    name: str | None,
    evaluation_type_id: int | None,
    referenced_eval_id: int | None,
    individual: int | None,
    evaluation_id: int
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        query = "UPDATE evaluations SET "
        params = []
        if classroom_id is not None:
            query += "classroom_id = %s, "
            params.append(classroom_id)
        if name is not None:
            query += "name = %s, "
            params.append(name)
        if evaluation_type_id is not None:
            query += "evaluation_type_id = %s, "
            params.append(evaluation_type_id)
        if referenced_eval_id is not None or evaluation_type_id is not None:
            query += "referenced_eval_id = %s, "
            params.append(referenced_eval_id)
        if individual is not None:
            query += "individual = %s, "
            params.append(individual)

        query = query.rstrip(", ")
        query += " WHERE id = %s"
        params.append(evaluation_id)

        conn.exec_driver_sql(query, tuple(params))
        conn.commit()
    return {"message": "Evaluacion actualizada exitosamente", "status": 200}