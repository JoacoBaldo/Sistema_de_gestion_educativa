import bcrypt

from src.db.classroom import (
    agregar_usuario_classroom,
    puede_gestionar_alumnos,
    usuario_en_classroom,
)
from src.db.constantes import ESTUDIANTE
from src.db.students import (
    actualizar_estudiante,
    crear_student_profile,
    email_existe_otro,
    es_estudiante_en_classroom,
    obtener_o_crear_carrera,
    obtener_user_id_por_email,
)
from src.funciones.errores import (
    CSV_ID_USUARIO_NO_ENCONTRADO,
    EMAIL_REQUERIDO,
    EMAIL_YA_EXISTE,
    ERROR_CONEXION,
    ESTUDIANTE_NO_EN_CLASSROOM,
    SIN_PERMISO_CREAR_ALUMNO,
    SIN_PERMISO_EDITAR_ALUMNO,
    USUARIO_YA_EN_CLASSROOM,
)
from src.funciones.user import create_user


def parsear_csv(contenido_texto: str) -> list[dict]:
    lineas = contenido_texto.split("\n")
    titulos = lineas[0].strip().split(",")

    filas = []
    for linea in lineas[1:]:
        linea_limpia = linea.strip()
        if not linea_limpia:
            continue
        valores = linea_limpia.split(",")
        filas.append(dict(zip(titulos, valores)))

    return filas


def cargar_estudiantes_csv(archivo, classroom_id: int) -> tuple:
    try:
        contenido_texto = archivo.read().decode("utf-8")
    except Exception:
        return None, ERROR_CONEXION

    usuarios = parsear_csv(contenido_texto)

    guardados = 0
    asociados = 0

    for u in usuarios:
        email = u.get("email")
        if not email:
            return None, EMAIL_REQUERIDO

        document = u.get("document", "").strip()
        career_name = u.get("career", "").strip()

        _, error = create_user(
            {
                "username": u.get("username"),
                "email": email,
                "password": document,
            }
        )
        usuario_nuevo = error is None
        if error and error != EMAIL_YA_EXISTE:
            return None, error

        try:
            user_id = obtener_user_id_por_email(str(email))
            if not user_id:
                return None, CSV_ID_USUARIO_NO_ENCONTRADO

            if usuario_nuevo:
                career_id = obtener_o_crear_carrera(career_name)
                crear_student_profile(user_id, document, career_id)
                guardados += 1

            if not usuario_en_classroom(classroom_id, user_id):
                agregar_usuario_classroom(classroom_id, user_id, ESTUDIANTE)
                asociados += 1
        except Exception:
            return None, ERROR_CONEXION

    return {
        "status": "ok",
        "mensaje": "Proceso de CSV finalizado",
        "cantidad_procesados": len(usuarios),
        "cantidad_creados": guardados,
        "cantidad_asociados": classroom_id and asociados,
    }, None


def crear_estudiante_en_classroom(
    classroom_id: int,
    caller_id: int,
    username: str,
    email: str,
    document: str,
    career: str,
) -> tuple:
    if not puede_gestionar_alumnos(classroom_id, caller_id):
        return None, SIN_PERMISO_CREAR_ALUMNO

    _, error = create_user({"username": username, "email": email, "password": document})
    usuario_nuevo = error is None
    if error and error != EMAIL_YA_EXISTE:
        return None, error

    user_id = obtener_user_id_por_email(email)
    if not user_id:
        return None, CSV_ID_USUARIO_NO_ENCONTRADO

    if usuario_nuevo:
        career_id = obtener_o_crear_carrera(career)
        crear_student_profile(user_id, document, career_id)
    elif usuario_en_classroom(classroom_id, user_id):
        return None, USUARIO_YA_EN_CLASSROOM

    agregar_usuario_classroom(classroom_id, user_id, ESTUDIANTE)
    return {"message": "Estudiante creado y asignado", "user_id": user_id}, None


def actualizar_estudiante_en_classroom(
    classroom_id: int,
    caller_id: int,
    user_id: int,
    username: str,
    email: str,
    document: str,
    career: str,
) -> tuple:
    if not puede_gestionar_alumnos(classroom_id, caller_id):
        return None, SIN_PERMISO_EDITAR_ALUMNO

    if not es_estudiante_en_classroom(classroom_id, user_id):
        return None, ESTUDIANTE_NO_EN_CLASSROOM

    if email_existe_otro(email, user_id):
        return None, EMAIL_YA_EXISTE

    career_id = obtener_o_crear_carrera(career)
    hashed = bcrypt.hashpw(document.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    actualizar_estudiante(user_id, username, email, hashed, document, career_id)

    return {"message": "Estudiante actualizado", "user_id": user_id}, None
