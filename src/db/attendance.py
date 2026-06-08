from datetime import datetime
from .conexion import obtener_conexion
from .constantes import ESTUDIANTE

def contar_eventos_classroom(classroom_id: int) -> int:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT COUNT(*) FROM attendance_events
            WHERE classroom_id = %s
            """,
            (classroom_id,),
        ).fetchone()
    return resultado[0] if resultado else 0


def obtener_inasistencias_por_alumno(classroom_id: int) -> list[dict]:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultados = conn.exec_driver_sql(
            """
            SELECT
                u.id        AS student_id,
                u.username  AS username,
                u.email     AS email,
                a.absense   AS inasistencias
            FROM classroom_users cu
            JOIN users u ON u.id = cu.user_id
            LEFT JOIN attendance_events ae
                ON ae.classroom_id = cu.classroom_id
            LEFT JOIN attendance a
                ON a.student_id = cu.user_id
                AND a.attendance_event_id = ae.id
            WHERE cu.classroom_id = %s
                AND cu.role_id = %s
            GROUP BY u.id, u.username, u.email
            """,
            (classroom_id, ESTUDIANTE),
        ).fetchall()
    return [
        {
            "student_id": f[0],
            "username": f[1],
            "email": f[2],
            "inasistencias": int(f[3]),
        }
        for f in resultados
    ]


def obtener_evento_por_token(token: str) -> dict | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT ae.id, ae.classroom_id, c.name, ae.created_at
            FROM attendance_events ae
            JOIN classrooms c ON ae.classroom_id = c.id
            WHERE ae.qr_token = %s AND ae.expires_at > NOW()
            LIMIT 1
            """,
            (token,)
        ).fetchone()
        
    if not resultado:
        return None
        
    return {
        "event_id": resultado[0],
        "classroom_id": resultado[1],
        "materia": resultado[2],
        "fecha": resultado[3].strftime("%d/%m/%Y") if resultado[3] else datetime.now().strftime("%d/%m/%Y"),
        "docente": "Profesor a cargo"
    }

def obtener_alumno_por_padron_aula(classroom_id: int, padron: str) -> int | None:
    engine = obtener_conexion()
    with engine.connect() as conn:
        resultado = conn.exec_driver_sql(
            """
            SELECT u.id 
            FROM users u
            JOIN classroom_users cu ON u.id = cu.user_id
            WHERE u.document = %s AND cu.classroom_id = %s AND cu.role_id = %s
            LIMIT 1
            """,
            (padron, classroom_id, ESTUDIANTE)
        ).fetchone()
        
    return resultado[0] if resultado else None

def registrar_presente_db(student_id: int, event_id: int):
    engine = obtener_conexion()
    with engine.connect() as conn:
        existente = conn.exec_driver_sql(
            "SELECT 1 FROM attendance WHERE student_id = %s AND attendance_event_id = %s",
            (student_id, event_id)
        ).fetchone()

        if existente:
            conn.exec_driver_sql(
                "UPDATE attendance SET absense = 0 WHERE student_id = %s AND attendance_event_id = %s",
                (student_id, event_id)
            )
        else:
            conn.exec_driver_sql(
                "INSERT INTO attendance (student_id, attendance_event_id, absense) VALUES (%s, %s, 0)",
                (student_id, event_id)
            )
        conn.commit()