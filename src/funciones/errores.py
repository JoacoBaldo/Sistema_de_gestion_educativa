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

SIN_PERMISO_LINK = {
    "error": "Solo PROFESOR o ADMINISTRADOR pueden compartir el link",
    "status": 403,
}

FECHA_NO_VALIDA = {
    "error": "Fecha no válida, debe ser en formato YYYY-MM-DD",
    "status": 400,
}
AULA_NO_VALIDA = {
    "error": "Aula no válida, debe ser una de las aulas permitidas",
    "status": 400,
}
CLASSROOM_NO_EXISTE = {"error": "El classroom especificado no existe", "status": 404}

CODIGO_REQUERIDO = {"error": "El código de asistencia es requerido", "status": 400}
CODIGO_INVALIDO = {
    "error": "El código de asistencia es inválido o ya expiró",
    "status": 400,
}
CODIGO_NO_CORRESPONDE = {
    "error": "Este código no corresponde a tu usuario",
    "status": 403,
}
DELTA_INVALIDO = {"error": "El campo 'delta' debe ser un entero", "status": 400}
DELTA_CERO = {"error": "El campo 'delta' no puede ser 0", "status": 400}

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
DATOS_EVALUACION_REQUERIDOS = {
    "error": "name y evaluation_type_id son requeridos",
    "status": 400,
}
TIPO_EVALUACION_INVALIDO = {
    "error": "El tipo de evaluación especificado no existe",
    "status": 404,
}
REFERENCED_EVAL_REQUERIDO = {
    "error": "referenced_eval_id es obligatorio para evaluaciones de tipo recuperatorio",
    "status": 400,
}
REFERENCED_EVAL_NO_EXISTE = {
    "error": "La evaluación referenciada no existe",
    "status": 404,
}
ERROR_ENVIO_MAIL = {
    "error": "Hubo un problema interno al intentar enviar el correo",
    "status": 500,
}
SIN_ESTUDIANTES = {
    "error": "No hay estudiantes en el aula",
    "status": 400,
}
SCHEDULE_REQUERIDO = {
    "error": "class_day (int), class_start, class_end y academic_period_id son requeridos",
    "status": 400,
}
LINK_INVALIDO = {"error": "El link es inválido o expiró", "status": 400}
USUARIO_YA_EN_CLASSROOM = {
    "error": "El usuario ya pertenece al classroom",
    "status": 409,
}
FILTRO_INVALIDO = {
    "error": "Filtro inválido. Valores permitidos: students, students_passed, teams, colaborators",
    "status": 400,
}
BODY_INVALIDO = {
    "error": "El body debe ser el JSON de respuesta del endpoint de métricas",
    "status": 400,
}
ARCHIVO_NO_ENVIADO = {
    "error": "No se envió ningún archivo con la clave 'archivo'",
    "status": 400,
}
ARCHIVO_VACIO = {"error": "El nombre del archivo está vacío", "status": 400}
ERROR_PROCESAMIENTO_CSV = {"error": "Error al procesar el archivo CSV", "status": 500}
EVALUACION_NO_EXISTE = {"error": "La evaluación especificada no existe", "status": 404}
EVALUATION_ID_REQUERIDO = {"error": "evaluation_id es requerido", "status": 400}
SESION_INVALIDA = {"error": "Sesión inválida. Vuelve a iniciar sesión.", "status": 401}
MIEMBROS_REQUERIDO = {"error": "Al menos un miembro es requerido", "status": 400}
CLASSROOM_NO_ESPECIFICADO = {"error": "Classroom no especificado", "status": 400}
EQUIPO_NO_CREADO = {"error": "No se pudo crear el equipo", "status": 500}
DATOS_ESTUDIANTE_REQUERIDOS = {
    "error": "username, email, document y career son requeridos",
    "status": 400,
}
SIN_PERMISO_CREAR_ALUMNO = {
    "error": "Solo PROFESOR, AYUDANTE o ADMINISTRADOR pueden agregar alumnos",
    "status": 403,
}
SIN_PERMISO_EDITAR_ALUMNO = {
    "error": "Solo PROFESOR, AYUDANTE o ADMINISTRADOR pueden editar alumnos",
    "status": 403,
}
ESTUDIANTE_NO_EN_CLASSROOM = {
    "error": "El usuario no es un estudiante de este classroom",
    "status": 404,
}
