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
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            INSERT INTO request_logs (
                usuario_id,
                metodo,
                path,
                status_code,
                remote_addr,
                user_agent,
                request_body
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                user_id,
                metodo,
                path,
                status_code,
                remote_addr,
                user_agent,
                request_body,
            ),
        )
        conn.commit()
