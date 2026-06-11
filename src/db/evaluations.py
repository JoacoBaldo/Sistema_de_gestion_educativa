from .conexion import obtener_conexion

EVALUATION_TYPE_LABELS = {
    1: ("parcial", "Parcial"),
    2: ("tp", "TP"),
    3: ("recuperatorio", "Recuperatorio"),
    4: ("parcialito", "Parcialito"),
}


def obtener_evaluaciones_classroom(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT id, name, evaluation_type_id, referenced_eval_id, individual, created_at
            FROM evaluations
            WHERE classroom_id = %s
            ORDER BY created_at DESC, id DESC
            """,
            (classroom_id,),
        ).fetchall()

    evaluaciones = []
    for fila in resultados:
        tipo_id = fila[2]
        tipo_slug, tipo_nombre = EVALUATION_TYPE_LABELS.get(
            tipo_id, ("otro", f"Tipo {tipo_id}")
        )
        created_at = fila[5]
        fecha = str(created_at)[:10] if created_at else ""
        evaluaciones.append(
            {
                "id": fila[0],
                "name": fila[1],
                "evaluation_type_id": tipo_id,
                "tipo_slug": tipo_slug,
                "tipo_nombre": tipo_nombre,
                "referenced_eval_id": fila[3],
                "individual": bool(fila[4]),
                "created_at": created_at,
                "fecha": fecha,
            }
        )
    return evaluaciones


def crear_evaluacion_db(
    classroom_id: int,
    name: str,
    evaluation_type_id: int,
    referenced_eval_id: int | None,
    individual: int,
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO evaluations (
                classroom_id, name, evaluation_type_id, referenced_eval_id, individual
            ) VALUES (%s, %s, %s, %s, %s)
            """,
            (classroom_id, name, evaluation_type_id, referenced_eval_id, individual),
        )
        conn.commit()
        evaluation_id = cursor.lastrowid
    return {
        "message": "Evaluacion creada exitosamente",
        "status": 201,
        "id": evaluation_id,
    }


def existe_evaluation_type(evaluation_type_id: int) -> bool:
    return evaluation_type_id in EVALUATION_TYPE_LABELS


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
        resultado = (
            conn.exec_driver_sql(
                "SELECT id, classroom_id, name, evaluation_type_id, referenced_eval_id, individual FROM evaluations WHERE id = %s LIMIT 1",
                (evaluation_id,),
            )
            .mappings()
            .fetchone()
        )
    return dict(resultado) if resultado else None


def actualizar_evaluacion_db(
    classroom_id: int | None,
    name: str | None,
    evaluation_type_id: int | None,
    referenced_eval_id: int | None,
    individual: int | None,
    evaluation_id: int,
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        query = "UPDATE evaluations SET "
        params: list[str | int | None] = []
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

def eliminar_evaluacion_db(evaluation_id: int) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM evaluations 
            WHERE id = %s
            """,
            (evaluation_id,),
        )
        conn.commit()
    return {"message": "Evaluación eliminada exitosamente", "status": 200}