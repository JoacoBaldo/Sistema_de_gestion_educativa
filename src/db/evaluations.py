import re

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
            SELECT id, name, evaluation_type_id, referenced_eval_id, individual, created_at, due_date
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

        due_date_raw = fila[6]
        fecha_entrega = str(due_date_raw)[:10] if due_date_raw else ""

        evaluaciones.append(
            {
                "id": fila[0],
                "name": fila[1],
                "evaluation_type_id": tipo_id,
                "tipo_slug": tipo_slug,
                "tipo_nombre": tipo_nombre,
                "individual": bool(fila[4]),
                "fecha": fecha_entrega,
                "created_at": str(fila[5])[:10] if fila[5] else "",
            }
        )
    return evaluaciones


def evaluacion_tiene_notas_db(evaluation_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM grades WHERE evaluation_id = %s LIMIT 1", (evaluation_id,)
        ).fetchone()
    return resultado is not None


def guardar_nota_individual_o_equipo_db(
    evaluation_id: int,
    score: float,
    user_id: int | None = None,
    team_id: int | None = None,
) -> dict:
    engine = obtener_conexion()
    query_upsert = """
        INSERT INTO grades (user_id, evaluation_id, score, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON DUPLICATE KEY UPDATE 
            score = VALUES(score),
            updated_at = NOW()
    """
    with engine.connect() as conn:
        transaccion = conn.begin()
        try:
            if user_id is not None:
                conn.exec_driver_sql(query_upsert, (user_id, evaluation_id, score))
            elif team_id is not None:
                miembros = conn.exec_driver_sql(
                    "SELECT user_id FROM team_members WHERE team_id = %s", (team_id,)
                ).fetchall()
                for m in miembros:
                    conn.exec_driver_sql(query_upsert, (m[0], evaluation_id, score))

            transaccion.commit()
            return {"message": "Calificación registrada correctamente", "status": 201}
        except Exception as e:
            transaccion.rollback()
            raise e


def crear_evaluacion_db(
    classroom_id: int,
    name: str,
    evaluation_type_id: int,
    referenced_eval_id: int | None,
    individual: int,
    due_date: str | None,
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO evaluations (
                classroom_id, name, evaluation_type_id, referenced_eval_id, individual, due_date
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                classroom_id,
                name,
                evaluation_type_id,
                referenced_eval_id,
                individual,
                due_date if due_date and due_date.strip() != "" else None,
            ),
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
                "SELECT id, classroom_id, name, evaluation_type_id, referenced_eval_id, individual, due_date FROM evaluations WHERE id = %s LIMIT 1",
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
    due_date: str | None,  # Agregado al endpoint de actualización
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
        if due_date is not None:
            query += "due_date = %s, "
            params.append(due_date if due_date.strip() != "" else None)

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


def procesar_notas_masivas_db(
    classroom_id: int, evaluation_id: int, lista_notas: list[dict]
) -> dict:
    engine = obtener_conexion()
    inserted_count = 0

    query_buscar_alumno = """
        SELECT u.id 
        FROM users u
        LEFT JOIN student_profiles sp ON sp.user_id = u.id
        JOIN classroom_users cu ON cu.user_id = u.id
        WHERE cu.classroom_id = %s 
          AND (sp.document = %s OR u.email = %s)
        LIMIT 1
    """

    query_buscar_equipo = """
        SELECT tu.user_id 
        FROM teams t
        JOIN team_members tu ON tu.team_id = t.id
        WHERE t.classroom_id = %s AND t.name = %s
    """

    query_upsert_nota = """
        INSERT INTO grades (user_id, evaluation_id, score, created_at, updated_at)
        VALUES (%s, %s, %s, NOW(), NOW())
        ON DUPLICATE KEY UPDATE 
            score = VALUES(score),
            updated_at = NOW()
    """

    with engine.connect() as conn:
        transaccion = conn.begin()
        try:
            for item in lista_notas:
                nota = item["score"]

                if "user_id" in item:
                    conn.exec_driver_sql(
                        query_upsert_nota, (item["user_id"], evaluation_id, nota)
                    )
                    inserted_count += 1
                    continue

                identificador = item.get("identifier")
                if not identificador:
                    continue

                identificador_limpio = re.sub(r"\s+", " ", str(identificador)).strip()

                tipo = item.get("type", "documento")

                if tipo == "equipo":
                    integrantes = conn.exec_driver_sql(
                        query_buscar_equipo, (classroom_id, identificador_limpio)
                    ).fetchall()

                    for integrante in integrantes:
                        user_id = integrante[0]
                        conn.exec_driver_sql(
                            query_upsert_nota, (user_id, evaluation_id, nota)
                        )
                        inserted_count += 1
                else:
                    alumno = conn.exec_driver_sql(
                        query_buscar_alumno,
                        (classroom_id, identificador_limpio, identificador_limpio),
                    ).fetchone()
                    if alumno:
                        user_id = alumno[0]
                        conn.exec_driver_sql(
                            query_upsert_nota, (user_id, evaluation_id, nota)
                        )
                        inserted_count += 1

            transaccion.commit()
            return {"inserted": inserted_count, "error": None}

        except Exception as e:
            transaccion.rollback()
            return {"inserted": 0, "error": str(e)}


def actualizar_nota_estudiante_db(
    evaluation_id: int, user_id: int, score: float
) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO grades (user_id, evaluation_id, score, created_at, updated_at)
            VALUES (%s, %s, %s, NOW(), NOW())
            ON DUPLICATE KEY UPDATE 
                score = VALUES(score),
                updated_at = NOW()
            """,
            (user_id, evaluation_id, score),
        )
        conn.commit()
    return {"message": "Calificación actualizada exitosamente", "status": 200}


def eliminar_nota_estudiante_db(evaluation_id: int, user_id: int) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "DELETE FROM grades WHERE evaluation_id = %s AND user_id = %s",
            (evaluation_id, user_id),
        )
        conn.commit()
    return {"message": "Calificación eliminada exitosamente", "status": 200}
