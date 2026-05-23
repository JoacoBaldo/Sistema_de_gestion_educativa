from .conexion import obtener_conexion
from .roles import PROFESOR, ADMINISTRADOR


def obtener_profesores(classroom_id: int) -> list:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT u.id, u.username, u.email, cu.role_id
            FROM classroom_users cu
            JOIN users u ON cu.user_id = u.id
            WHERE cu.classroom_id = %s
            """,
            (classroom_id,),
        ).fetchall()

    profesores = []
    for fila in resultados:
        profesores.append(
            {
                "id": fila[0],
                "username": fila[1],
                "email": fila[2],
                "role_id": fila[3],
            }
        )
    return profesores


def profesor_existe_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            LIMIT 1
            """,
            (classroom_id, usuario_id),
        ).fetchone()

    return resultado is not None


def es_admin_classroom(classroom_id: int, usuario_id: int) -> bool:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT 1 FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s AND role_id IN (%s, %s)
            LIMIT 1
            """,
            (classroom_id, usuario_id, ADMINISTRADOR, PROFESOR),
        ).fetchone()

    return resultado is not None

def eliminar_usuario_classroom(classroom_id: int, usuario_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        conn.exec_driver_sql(
            """
            DELETE FROM classroom_users
            WHERE classroom_id = %s AND user_id = %s
            """,
            (classroom_id, usuario_id),
        )
        conn.commit()
