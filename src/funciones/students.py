import logging

from src.db.classroom import agregar_usuario_classroom, usuario_en_classroom
from src.db.constantes import ESTUDIANTE
from src.db.students import (
    obtener_o_crear_carrera,
    obtener_user_id_por_email,
)
from src.funciones.errores import EMAIL_YA_EXISTE, ERROR_AGREGAR_ESTUDIANTE, ESTUDIANTE_NO_EXISTE, REQUIERE_EMAIL_O_ID, USUARIO_YA_EN_CLASSROOM, ERROR_PROCESAMIENTO_CSV
from src.funciones.user import create_user, usuario_existe


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
    except Exception as e:
        logging.error("Error al leer el archivo CSV: %s", e)
        from src.funciones.errores import ERROR_PROCESAMIENTO_CSV

        return None, ERROR_PROCESAMIENTO_CSV

    usuarios = parsear_csv(contenido_texto)

    guardados = 0
    asociados = 0
    errores = []

    for u in usuarios:
        email = u.get("email")
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
            errores.append({"usuario": email, "error": error})
            continue

        try:
            user_id = obtener_user_id_por_email(email)

            if usuario_nuevo:
                career_id = obtener_o_crear_carrera(career_name)
                crear_student_profile(user_id, document, career_id)
                guardados += 1

            if not usuario_en_classroom(classroom_id, user_id):
                agregar_usuario_classroom(classroom_id, user_id, ESTUDIANTE)
                asociados += 1
        except Exception as e:
            logging.error("Error al procesar el estudiante %s: %s", email, e)
            errores.append(
                {"usuario": email, "error": "Error al procesar el estudiante"}
            )

    return {
        "status": "ok",
        "mensaje": "Proceso de CSV finalizado",
        "cantidad_procesados": len(usuarios),
        "cantidad_creados": guardados,
        "cantidad_asociados": classroom_id and asociados,
        "errores": errores,
    }, None


def agregar_estudiante_existente_classroom(
    classroom_id: int, student_id: int = None, email: str = None
) -> tuple:
    
    if not student_id and not email:
        return None, REQUIERE_EMAIL_O_ID
    
    if email:
        student_id = obtener_user_id_por_email(email)
        if not student_id:
            return None, ESTUDIANTE_NO_EXISTE
    elif student_id:
        usuario, error = usuario_existe(student_id)
        if error:
            return None, ESTUDIANTE_NO_EXISTE
    
    if usuario_en_classroom(classroom_id, student_id):
        return None, USUARIO_YA_EN_CLASSROOM
    
    try:
        agregar_usuario_classroom(classroom_id, student_id, ESTUDIANTE)
        return {
            "status": 201,
            "mensaje": "Estudiante agregado al classroom exitosamente",
        }, None
    except Exception as e:
        logging.error("Error al agregar estudiante al classroom: %s", e)
        return None, ERROR_AGREGAR_ESTUDIANTE

