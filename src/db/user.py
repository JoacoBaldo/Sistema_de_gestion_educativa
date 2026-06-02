from .conexion import obtener_conexion


def create_User_db(user: dict) -> dict:
    engine = obtener_conexion()

    with engine.connect() as conn:
        conn.exec_driver_sql(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (user["username"], user["email"], user["password"]),
        )
        conn.commit()
        return {"message": "User created successfully", "status_code": 201}

    conn.close()


def email_exists(email: str) -> bool:
    engine = obtener_conexion()

    with engine.connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT 1 FROM users WHERE email = %s LIMIT 1"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
        return result is not None

    conn.close()


def get_user_id_by_email(email: str) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        with conn.cursor() as cursor:
            sql = "SELECT id FROM users WHERE email = %s"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
    if not result:
        return {"error": "Email not found", "status_code": 404}
    return {"user_id": result[0], "status_code": 200}
