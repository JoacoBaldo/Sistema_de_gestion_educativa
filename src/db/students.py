from src.db.conexion import obtener_conexion
from src.db.constantes import ESTUDIANTE
from src.db.user import crear_usuario_db, email_existe

__all__ = ["crear_usuario_db", "email_existe"]


def obtener_user_id_por_email(email: str) -> int | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT id FROM users WHERE email = %s LIMIT 1",
            (email,),
        ).fetchone()
    return resultado[0] if resultado else None


def obtener_o_crear_carrera(name: str) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT id FROM careers WHERE name = %s LIMIT 1",
            (name,),
        ).fetchone()
        if resultado:
            return resultado[0]
        conn.exec_driver_sql(
            "INSERT INTO careers (name) VALUES (%s)",
            (name,),
        )
        conn.commit()
        career_id = conn.exec_driver_sql("SELECT LAST_INSERT_ID()").fetchone()[0]
    return career_id


def crear_student_profile(user_id: int, document: str, career_id: int) -> None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            "INSERT INTO student_profiles (user_id, document, career_id) VALUES (%s, %s, %s)",
            (user_id, document, career_id),
        )
        conn.commit()


def es_estudiante_en_classroom(classroom_id: int, user_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM classroom_users WHERE classroom_id = %s AND user_id = %s AND role_id = %s LIMIT 1",
            (classroom_id, user_id, ESTUDIANTE),
        ).fetchone()
    return resultado is not None


def email_existe_otro(email: str, user_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            "SELECT 1 FROM users WHERE email = %s AND id != %s LIMIT 1",
            (email, user_id),
        ).fetchone()
    return resultado is not None


def actualizar_estudiante(
    user_id: int, username: str, email: str, password_hasheada: str, document: str, career_id: int
) -> None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            UPDATE users u
            JOIN student_profiles sp ON sp.user_id = u.id
            SET u.username = %s, u.email = %s, u.password = %s,
                sp.document = %s, sp.career_id = %s
            WHERE u.id = %s
            """,
            (username, email, password_hasheada, document, career_id, user_id),
        )
        conn.commit()
