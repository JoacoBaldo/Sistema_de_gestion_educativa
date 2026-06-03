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


def obtener_id_por_email(email: str) -> int | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT id FROM users WHERE email = %s",
            (email,),
        ).fetchone()
    if not resultado:
        return None
    return resultado[0]


def actualizar_alumno_db(user_id: int, datos_nuevos: dict) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE users 
            SET username = %s, email = %s, document = %s 
            WHERE id = %s
            """,
            (datos_nuevos["username"], datos_nuevos["email"], datos_nuevos["document"], user_id)
        )
        conn.commit()
        
    datos_nuevos['id'] = user_id
    datos_nuevos['career'] = "Ingenieria informatica"
    datos_nuevos['GPA'] = 7.6
    datos_nuevos['status'] = "activo"
    
    return datos_nuevos


def crear_alumno_db(datos_estudiante: dict) -> dict:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            INSERT INTO users (username, email, document, career) 
            VALUES (%s, %s, %s, %s) RETURNING id
            """,
            (datos_estudiante["username"], datos_estudiante["email"], 
             datos_estudiante["document"], datos_estudiante["career"])
        )
        nuevo_id = resultado.fetchone()[0]
        conn.commit()
        
    datos_estudiante['id'] = nuevo_id
    datos_estudiante['status'] = "activo"
    
    return datos_estudiante