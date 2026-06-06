from src.db import classroom as db_classroom
from .errores import SIN_ACCESO


def subir_contenido_classroom(
    classroom_id: int, titulo: str, url: str, usuario_id: int
) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    resultado_simulado = {
        "id": 101,
        "classroom_id": classroom_id,
        "title": titulo,
        "url": url,
        "uploaded_by": usuario_id,
        "message": "Contenido de Drive registrado exitosamente",
    }

    return resultado_simulado, None


def eliminar_contenido_classroom(
    classroom_id: int, contenido_id: int, usuario_id: int
) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    return {"message": f"Contenido con ID {contenido_id} eliminado correctamente"}, None
