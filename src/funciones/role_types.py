from src.db.role_types import obtener_role_types
from src.funciones.errores import ERROR_CONEXION


def listar_role_types() -> tuple:
    try:
        return obtener_role_types(), None
    except Exception:
        return None, ERROR_CONEXION
