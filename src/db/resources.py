from .conexion import obtener_conexion


def obtener_recursos_por_aula(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT id, name, resource_type, link, created_at 
            FROM resources 
            WHERE classroom_id = %s
            ORDER BY created_at DESC
            """,
            (classroom_id,),
        ).fetchall()

    return [
        {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "link": row[3],
            "created_at": row[4].strftime("%d/%m/%Y") if row[4] else "",
        }
        for row in resultados
    ]
