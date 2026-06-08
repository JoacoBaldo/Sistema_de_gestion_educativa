import logging

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


def cargar_estudiantes_csv(archivo) -> tuple:
    try:
        contenido_texto = archivo.read().decode("utf-8")
    except Exception as e:
        logging.error("Error al leer el archivo CSV: %s", e)
        from src.funciones.errores import ERROR_PROCESAMIENTO_CSV

        return None, ERROR_PROCESAMIENTO_CSV

    usuarios = parsear_csv(contenido_texto)

    guardados = 0
    errores = []

    for u in usuarios:
        resultado, error = create_user(
            {
                "username": u.get("username"),
                "email": u.get("email"),
                "password": u.get("password"),
            }
        )
        if error:
            errores.append({"usuario": u.get("email"), "error": error})
        else:
            guardados += 1

    return {
        "status": "ok",
        "mensaje": "Proceso de CSV finalizado",
        "cantidad_procesados": len(usuarios),
        "cantidad_guardados_ok": guardados,
        "errores": errores,
    }, None
