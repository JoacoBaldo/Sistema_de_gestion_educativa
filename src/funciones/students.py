from src.db.classroom import agregar_usuario_classroom, puede_gestionar_alumnos, usuario_en_classroom
from src.db.constantes import ESTUDIANTE
from src.db.students import (
    crear_student_profile,
    crear_estudiante_completo,
    obtener_o_crear_carrera,
    obtener_user_id_por_email,
)
from src.funciones.errores import (
    DATOS_ESTUDIANTE_REQUERIDOS,
    EMAIL_YA_EXISTE,
    SIN_PERMISO_CREAR_ALUMNO,
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


def crear_estudiante_en_classroom(
    classroom_id: int, caller_id: int, username: str, email: str, document: str, career: str
) -> tuple:
    if not puede_gestionar_alumnos(classroom_id, caller_id):
        return None, SIN_PERMISO_CREAR_ALUMNO

    resultado, error = create_user(
        {"username": username, "email": email, "password": document}
    )
    usuario_nuevo = error is None
    if error and error != EMAIL_YA_EXISTE:
        return None, error

    user_id = obtener_user_id_por_email(email)

    if usuario_nuevo:
        career_id = obtener_o_crear_carrera(career)
        user_id, db_error = crear_estudiante_completo(
            username, email, resultado["password"], document, career_id, classroom_id
        )
        if db_error:
            return None, {"error": db_error, "status": 500}
    else:
        if usuario_en_classroom(classroom_id, user_id):
            return None, USUARIO_YA_EN_CLASSROOM
        agregar_usuario_classroom(classroom_id, user_id, ESTUDIANTE)

    return {"message": "Estudiante creado y asignado", "user_id": user_id}, None
