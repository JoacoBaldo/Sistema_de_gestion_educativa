from src.db import classroom as db_classroom
from src.db import resources as db_resources
from src.db.classroom import usuario_en_classroom

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
    tipo_recurso: str = "enlace",
) -> tuple:
    try:
        nuevo_id = db_resources.guardar_contenido_classroom(
            classroom_id, titulo, tipo_recurso, url, usuario_id
        )
        # Retornamos el éxito
        return {"message": "Recurso subido", "id": nuevo_id}, None
    except Exception as e:
        # Agregamos 'status' para evitar el KeyError en utils.py
        return None, {"error": str(e), "status": 500}


def eliminar_contenido_classroom(
    classroom_id: int, contenido_id: int, usuario_id: int
) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    db_resources.eliminar_contenido_classroom(contenido_id)

    return {"message": f"Contenido con ID {contenido_id} eliminado correctamente"}, None


def editar_contenido_classroom(
    classroom_id: int,
    contenido_id: int,
    titulo: str,
    tipo: str,
    url: str,
    usuario_id: int,
):
    try:
        db_resources.actualizar_contenido_db(contenido_id, titulo, tipo, url)

        return {"mensaje": "Contenido actualizado con éxito", "id": contenido_id}, None
    except Exception as e:
        error_estructurado = {"error": f"ERROR_BASE_DE_DATOS: {str(e)}", "status": 500}
        return None, error_estructurado
