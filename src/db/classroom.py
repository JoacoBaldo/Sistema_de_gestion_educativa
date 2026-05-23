from sqlalchemy import text
from .conexion import obtener_conexion

def obtener_profesores(classroom_id: int) -> list:
    engine = obtener_conexion()
    query = text("""
        SELECT u.id, u.username, u.email, cu.created_at
        FROM classroom_users cu
        JOIN users u ON cu.user_id = u.id
        WHERE cu.classroom_id = :classroom_id AND cu.role_id = 0
    """)
    with engine.connect() as conn:
        resultados = conn.execute(query, {"classroom_id": classroom_id}).fetchall()

    profesores = []
    for fila in resultados:
        profesores.append({
            "id": fila[0],
            "username": fila[1],
            "email": fila[2],
            "joined_at": fila[3].isoformat() if fila[3] else None
        })
    return profesores

def tiene_acceso_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    query = text("""
        SELECT 1 FROM classroom_users
        WHERE classroom_id = :classroom_id AND user_id = :user_id
        UNION
        SELECT 1 FROM classrooms
        WHERE id = :classroom_id AND user_id = :user_id
        LIMIT 1
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {
            "classroom_id": classroom_id,
            "user_id": usuario_id
        }).fetchone()

    return resultado is not None

def es_admin_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    query = text("""
        SELECT 1 FROM classroom_users
        WHERE classroom_id = :classroom_id AND user_id = :user_id AND role_id = 1
        UNION
        SELECT 1 FROM classrooms
        WHERE id = :classroom_id AND user_id = :user_id
        LIMIT 1
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {
            "classroom_id": classroom_id,
            "user_id": usuario_id
        }).fetchone()

    return resultado is not None

def usuario_en_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    query = text("""
        SELECT 1 FROM classroom_users
        WHERE classroom_id = :classroom_id AND user_id = :user_id
        LIMIT 1
    """)
    with engine.connect() as conn:
        resultado = conn.execute(query, {
            "classroom_id": classroom_id,
            "user_id": usuario_id
        }).fetchone()

    return resultado is not None

def eliminar_usuario_classroom(classroom_id: int, usuario_id: int):
    engine = obtener_conexion()
    query = text("""
        DELETE FROM classroom_users
        WHERE classroom_id = :classroom_id AND user_id = :user_id
    """)
    with engine.connect() as conn:
        conn.execute(query, {
            "classroom_id": classroom_id,
            "user_id": usuario_id
        })
        conn.commit()
