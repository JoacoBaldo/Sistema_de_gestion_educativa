from .conexion import obtener_conexion


def obtener_role_types() -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            "SELECT id, name FROM role_types ORDER BY id"
        ).fetchall()
    return [{"id": f[0], "name": f[1]} for f in resultados]
