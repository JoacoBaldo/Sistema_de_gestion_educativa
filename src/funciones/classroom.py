from src.db import classroom as db_classroom
from .errores import SIN_ACCESO, NO_ES_ADMIN, USUARIO_NO_EXISTE


def obtener_profesores_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.tiene_acceso_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    profesores = db_classroom.obtener_profesores(classroom_id)
    return profesores, None


def eliminar_usuario_classroom(
    classroom_id: int, usuario_id: int, usuario_id_requester: int
) -> tuple:
    if not db_classroom.es_admin_classroom(classroom_id, usuario_id_requester):
        return None, NO_ES_ADMIN

    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, USUARIO_NO_EXISTE

    db_classroom.eliminar_usuario_classroom(classroom_id, usuario_id)
    return {"message": "User removed from classroom"}, None
