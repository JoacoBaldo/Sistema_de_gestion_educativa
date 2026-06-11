from src.db.conexion import obtener_conexion

SIN_ACCESO = {"error": "No tienes acceso a esta aula"}


def obtener_recursos_por_aula(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = (
            conn.exec_driver_sql(
                """
            SELECT 
                r.id, 
                r.Title AS name, 
                COALESCE(ft.name, 'link') AS resource_type, 
                r.link, 
                r.created_at
            FROM resourses r
            LEFT JOIN file_types ft ON r.file_type_id = ft.id
            WHERE r.classroom_id = %s
            ORDER BY r.created_at DESC
            """,
                (classroom_id,),
            )
            .mappings()
            .all()
        )
        return [dict(row) for row in resultados]


def guardar_contenido_classroom(
    classroom_id: int, titulo: str, url: str, usuario_id: int
) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO resources (classroom_id, name, resource_type, link, created_at)
            VALUES (%s, %s, %s, %s, NOW())
            RETURNING id
            """,
            (classroom_id, titulo, "link", url),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()

    return nuevo_id


def eliminar_contenido_classroom(contenido_id: int) -> None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM resources 
            WHERE id = %s
            """,
            (contenido_id,),
        )
        conn.commit()
