TOKEN_INVALIDO = {"error": "Token inválido o expirado", "status": 401}
SIN_ACCESO = {"error": "No tiene acceso a este classroom", "status": 403}
NO_ES_ADMIN = {"error": "Se requiere rol Admin", "status": 403}
USUARIO_NO_EXISTE = {"error": "Usuario no existe en el classroom", "status": 404}

EMAIL_NO_EXISTE = {
    "error": "El email ingresado no esta en la base de datos",
    "status_code": 404,
}
EMAIL_NO_VALIDO = {"error": "Email must end with @fi.uba.ar", "status_code": 400}
EMAIL_YA_EXISTE = {"error": "User with this email already exists", "status_code": 409}

CONTRASENA_DEBIL = {
    "error": "La contraseña debe tener al menos 6 caracteres",
    "status_code": 400,
}

SIN_PERMISO_LINK = {
    "error": "Solo PROFESOR o ADMINISTRADOR pueden compartir el link",
    "status": 403,
}


FECHA_NO_VALIDA = {
    "error": "Fecha no válida, debe ser en formato YYYY-MM-DD",
    "status_code": 400,
}
AULA_NO_VALIDA = {
    "error": "Aula no válida, debe ser una de las aulas permitidas",
    "status_code": 400,
}
CLASSROOM_NO_EXISTE = {
    "error": "El classroom especificado no existe",
    "status_code": 404,
}
