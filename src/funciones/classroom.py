from datetime import datetime, timedelta

from src.db import auth as db_auth
from src.db import classroom as db_classroom
from .errores import SIN_ACCESO, NO_ES_ADMIN, USUARIO_NO_EXISTE
from .auth import TIEMPO_EXPIRACION

def obtener_profesores_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.profesor_existe_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    profesores = db_classroom.obtener_profesores(classroom_id)
    return profesores, None


def eliminar_usuario_classroom(
    classroom_id: int, usuario_id: int, usuario_id_requester: int
) -> tuple:
    if not db_classroom.es_admin_classroom(classroom_id, usuario_id_requester):
        return None, NO_ES_ADMIN

    if not db_classroom.profesor_existe_classroom(classroom_id, usuario_id):
        return None, USUARIO_NO_EXISTE

    db_classroom.eliminar_usuario_classroom(classroom_id, usuario_id)
    return {"message": "User removed from classroom"}, None


def obtener_link_classroom(classroom_id: int, usuario_id: int, role_id: int) -> tuple:
    if not db_classroom.es_admin_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION)
    token = db_auth.generar_link_classroom(classroom_id, role_id, expira_en)

    return {
        "join_link": f"/api/v1/login/join?={token}"
    }, None
