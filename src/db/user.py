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


def change_password_db(new_password_data: dict) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE users
            SET password = %s
            WHERE id = %s
            """,
            (new_password_data["new_password"], new_password_data["user_id"]),
        )
        conn.commit()

    return {"message": "Password changed successfully", "status_code": 200}
