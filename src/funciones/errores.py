TOKEN_INVALIDO = {"error": "Token inválido o expirado", "status": 401}
SIN_ACCESO = {"error": "No tiene acceso a este classroom", "status": 403}
NO_ES_ADMIN = {"error": "Se requiere rol Admin", "status": 403}
USUARIO_NO_EXISTE = {"error": "Usuario no existe en el classroom", "status": 404}
SIN_PERMISO_LINK = {
    "error": "Solo PROFESOR o ADMINISTRADOR pueden compartir el link",
    "status": 403,
}
EQUIPO_NO_EXISTE = {"error": "Equipo no encontrado", "status": 404}
MIEMBROS_INVALIDOS = {
    "error": "Uno o más miembros no pertenecen al aula",
DATOS_INVALIDOS = {
    "error": "name, department y university son requeridos",
    "status": 400,
}
