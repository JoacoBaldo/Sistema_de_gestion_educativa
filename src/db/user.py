from .conexion import cursor_db


def crear_usuario_db(user: dict) -> dict:
    with cursor_db(commit=True) as cur:
        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
            (user["username"], user["email"], user["password"]),
        )
    return {"message": "User created successfully", "status": 201}


def email_existe(email: str) -> bool:
    with cursor_db() as cur:
        cur.execute(
            "SELECT 1 FROM users WHERE email = %s LIMIT 1",
            (email,),
        )
        return cur.fetchone() is not None


def obtener_id_por_email(email: str) -> int | None:
    with cursor_db() as cur:
        cur.execute(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        )
        resultado = cur.fetchone()
    if not resultado:
        return None
    return resultado["id"]
