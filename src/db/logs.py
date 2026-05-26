from .conexion import obtener_conexion


def guardar_log(
    metodo: str,
    path: str,
    status_code: int,
    remote_addr: str | None,
    user_id: int | None,
    user_agent: str | None,
    request_body: str | None,
):
    # El registro de peticiones no está soportado en la base de datos actual.
    # Las sesiones se guardan en sesiones_activas, por lo que esta función
    # no debe intentar usar la tabla request_logs.
    return
