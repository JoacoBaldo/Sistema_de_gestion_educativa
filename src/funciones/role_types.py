from src.db.role_types import obtener_role_types


def listar_role_types() -> tuple:
    try:
        return obtener_role_types(), None
    except Exception as e:
        return None, {"error": str(e), "status": 500}
