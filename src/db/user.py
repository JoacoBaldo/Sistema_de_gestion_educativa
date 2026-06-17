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


def actualizar_contraseña(user_id: int, password_hash: str) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "UPDATE users SET password = %s WHERE id = %s",
            (password_hash, user_id),
        )
        conn.commit()
    return {"message": "Password updated successfully", "status": 200}


def email_existe(email: str) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM users WHERE email = %s LIMIT 1",
            (email,),
        ).fetchone()
    return resultado is not None
