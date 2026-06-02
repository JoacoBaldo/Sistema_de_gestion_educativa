TOKEN_INVALIDO = {"error": "Token inválido o expirado", "status": 401}
SIN_ACCESO = {"error": "No tiene acceso a este classroom", "status": 403}
NO_ES_ADMIN = {"error": "Se requiere rol Admin", "status": 403}
USUARIO_NO_EXISTE = {"error": "Usuario no existe en el classroom", "status": 404}
USUARIO_NO_EXISTE_GLOBAL = {"error": "Usuario no existe", "status": 404}

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
FALTAN_DATOS = {"error": "Faltan datos obligatorios", "status": 400}
EQUIPO_NO_EXISTE = {"error": "Equipo no encontrado", "status": 404}
MIEMBROS_INVALIDOS = {
    "error": "Uno o más miembros no pertenecen al aula",
    "status": 404,
}
DATOS_INVALIDOS = {
    "error": "name, department y university son requeridos",
    "status": 400,
}

CREDENCIALES_INVALIDAS = {"error": "Credenciales inválidas", "status": 401}
EMAIL_REQUERIDO = {"error": "email es requerido", "status": 400}
PASSWORD_REQUERIDO = {"error": "password es requerido", "status": 400}
USER_ID_NO_COINCIDE = {"error": "user_id no coincide", "status": 400}
