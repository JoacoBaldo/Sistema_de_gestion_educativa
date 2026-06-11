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
    classroom_id: int, titulo: str, tipo: str, url: str, usuario_id: int
) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        cursor = conn.exec_driver_sql(
            """
            INSERT INTO resourses (classroom_id, Title, file_type_id, link, created_at)
            VALUES (
                %s, 
                %s, 
                (SELECT id FROM file_types WHERE LOWER(name) LIKE CONCAT('%%', LOWER(%s), '%%') LIMIT 1), 
                %s, 
                NOW()
            )
            RETURNING id
            """,
            (classroom_id, titulo, tipo, url),
        )
        nuevo_id = cursor.fetchone()[0]
        conn.commit()

    return nuevo_id


def eliminar_contenido_classroom(contenido_id: int) -> None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM resourses 
            WHERE id = %s
            """,
            (contenido_id,),
        )
        conn.commit()

def actualizar_contenido_db(
    contenido_id: int, titulo: str, tipo: str, url: str
) -> None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE resourses 
            SET 
                Title = %s,
                link = %s,
                file_type_id = COALESCE(
                    (SELECT id FROM file_types WHERE LOWER(name) LIKE CONCAT('%%', LOWER(%s), '%%') LIMIT 1),
                    file_type_id
                )
            WHERE id = %s
            """,
            (titulo, url, tipo, contenido_id),
        )
        conn.commit()       
