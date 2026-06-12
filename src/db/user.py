from .conexion import obtener_conexion


def crear_usuario_db(user: dict) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (user["username"], user["email"], user["password"]),
        )
        conn.commit()
    return {"message": "User created successfully", "status": 201}


def email_existe(email: str) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM users WHERE email = %s LIMIT 1",
            (email,),
        ).fetchone()
    return resultado is not None


def usuario_existe_db(usuario_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        usuario = conn.exec_driver_sql(
            """
            SELECT id FROM users WHERE id = %s LIMIT 1;
            """,
            (usuario_id,),
        )
        return usuario.fetchone()
