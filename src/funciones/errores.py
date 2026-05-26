TOKEN_INVALIDO = {"error": "Token inválido o expirado", "status": 401}
SIN_ACCESO = {"error": "No tiene acceso a este classroom", "status": 403}
NO_ES_ADMIN = {"error": "Se requiere rol Admin", "status": 403}
USUARIO_NO_EXISTE = {"error": "Usuario no existe en el classroom", "status": 404}
EMAIL_NO_EXISTE = {
    "error": "El email ingresado no esta en la base de datos",
    "status": 404,
}
EMAIL_NO_VALIDO = {"error": "El email debe terminar en @fi.uba.ar", "status": 400}
EMAIL_YA_EXISTE = {"error": "Ya existe un usuario con ese email", "status": 409}
CONTRASENA_DEBIL = {
    "error": "La contraseña debe tener al menos 6 caracteres",
    "status": 400,
}

USUARIO_NO_EXISTE_GLOBAL = {"error": "Usuario no existe", "status": 404}
SIN_PERMISO_LINK = {
    "error": "Solo PROFESOR o ADMINISTRADOR pueden compartir el link",
    "status": 403,
}
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

ROLE_ID_REQUERIDO = {"error": "role_id es requerido", "status": 400}
ID_REQUERIDO = {"error": "id es requerido", "status": 400}
NAME_O_MIEMBROS_REQUERIDO = {"error": "Se requiere name o member_ids", "status": 400}
NAME_VACIO = {"error": "name no puede estar vacío", "status": 400}
MIEMBROS_NO_ES_LISTA = {"error": "member_ids debe ser una lista", "status": 400}
MIEMBROS_NO_INT = {"error": "member_ids debe contener enteros", "status": 400}
DATOS_USUARIO_REQUERIDOS = {
    "error": "username, email y password son requeridos",
    "status": 400,
}
ERROR_ENVIO_MAIL = {
    "error": "Hubo un problema interno al intentar enviar el correo",
    "status": 500,
}
FALTAN_DATOS = {"error": "Faltan datos obligatorios", "status": 400}
