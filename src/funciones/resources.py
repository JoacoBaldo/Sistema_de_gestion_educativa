from src.db import classroom as db_classroom
from src.db import resources as db_resources
from src.db.classroom import usuario_en_classroom
from src.db.conexion import obtener_conexion

SIN_ACCESO = {"error": "No tienes acceso a esta aula"}


def listar_recursos(classroom_id: int, usuario_id: int) -> tuple:
    if not usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    recursos = db_resources.obtener_recursos_por_aula(classroom_id)
    return recursos, None


def subir_contenido_classroom(
    classroom_id: int,
    titulo: str,
    url: str,
    usuario_id: int,
    tipo_recurso: str = "link",
) -> tuple:
    MAPEO_TIPOS = {"pdf": 1, "video": 2, "link": 3}
    file_type_id = MAPEO_TIPOS.get(tipo_recurso.lower(), 3)

    engine = obtener_conexion()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql(
                """
                INSERT INTO resourses (classroom_id, Title, link, file_type_id, created_at, updated_at)
                VALUES (%s, %s, %s, %s, NOW(), NOW())
                """,
                (classroom_id, titulo, url, file_type_id),
            )
            conn.commit()
        return {"message": "Recurso subido"}, None
    except Exception as e:
        return None, {"error": str(e)}


def eliminar_contenido_classroom(
    classroom_id: int, contenido_id: int, usuario_id: int
) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    db_resources.eliminar_contenido_classroom(contenido_id)

    return {"message": f"Contenido con ID {contenido_id} eliminado correctamente"}, None
