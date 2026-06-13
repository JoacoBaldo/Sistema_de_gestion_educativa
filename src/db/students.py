from src.db.conexion import obtener_conexion
from src.db.user import crear_usuario_db, email_existe
from .constantes import ESTUDIANTE
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


def crear_estudiante_completo(
    username: str,
    email: str,
    password_hash: str,
    document: str,
    career_id: int,
    classroom_id: int,
) -> tuple:

    engine = obtener_conexion()
    try:
        with engine.connect() as conn:
            conn.exec_driver_sql(
                "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                (username, email, password_hash),
            )
            conn.commit()

        user_id = obtener_user_id_por_email(email)

        with engine.connect() as conn:
            conn.exec_driver_sql(
                "INSERT INTO student_profiles (user_id, document, career_id) VALUES (%s, %s, %s)",
                (user_id, document, career_id),
            )

            conn.exec_driver_sql(
                "INSERT INTO classroom_users (classroom_id, user_id, role_id) VALUES (%s, %s, %s)",
                (classroom_id, user_id, ESTUDIANTE),
            )

            conn.commit()

        return user_id, None
    except Exception as e:
        return None, str(e)
