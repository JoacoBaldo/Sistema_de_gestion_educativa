from datetime import datetime, timedelta

from src.db import auth as db_auth
from src.db import classroom as db_classroom
from .constantes import TIEMPO_EXPIRACION_HORAS
from .errores import NO_ES_ADMIN, SIN_ACCESO, SIN_PERMISO_LINK, USUARIO_NO_EXISTE


def obtener_profesores_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    profesores = db_classroom.obtener_profesores(classroom_id)
    return profesores, None


def eliminar_usuario_classroom(
    classroom_id: int, usuario_id: int, usuario_id_requester: int
) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id_requester):
        return None, NO_ES_ADMIN

    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, USUARIO_NO_EXISTE

    db_classroom.eliminar_usuario_classroom(classroom_id, usuario_id)
    return {"message": "User removed from classroom"}, None


def obtener_link_classroom(classroom_id: int, usuario_id: int, role_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, SIN_PERMISO_LINK

    expira_en = datetime.now() + timedelta(hours=TIEMPO_EXPIRACION_HORAS)

    token = db_auth.token_classroom_existe(classroom_id, role_id)
    if token:
        db_auth.actualizar_link_classroom(token, expira_en)
    else:
        token = db_auth.generar_link_classroom(classroom_id, role_id, expira_en)

    return {"join_link": f"/api/v1/login/join?token={token}"}, None


def obtener_periodos_academicos() -> tuple:
    periodos = db_classroom.obtener_todos_los_periodos()
    return periodos, None


def crear_nueva_classroom(
    name: str,
    department: str,
    university: str,
    usuario_id: int,
    class_day: str,
    class_start: str,
    class_end: str,
    academic_period_id: int,
) -> tuple:
    inserted_id = db_classroom.guardar_classroom(name, department, university)
    schedule_id = db_classroom.guardar_class_schedule(
        inserted_id, int(class_day), class_start, class_end, academic_period_id
    )
    db_classroom.asignar_admin_classroom(inserted_id, usuario_id)
    return {
        "id": inserted_id,
        "name": name,
        "department": department,
        "university": university,
        "schedule": {
            "id": schedule_id,
            "class_day": class_day,
            "class_start": class_start,
            "class_end": class_end,
            "academic_period_id": academic_period_id,
        },
    }, None


def obtener_lista_classrooms(usuario_id: int) -> tuple:
    classrooms = db_classroom.obtener_classrooms_usuario(usuario_id)
    return classrooms, None
