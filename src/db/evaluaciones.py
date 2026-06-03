from .conexion import cursor_db


def crear_evaluacion_db(classroom_id: int, fecha: str, aulas: tuple) -> dict:
    with cursor_db(commit=True) as cur:
        cur.execute(
            "INSERT INTO evaluaciones (classroom_id, fecha, aula) VALUES (%s, %s, %s)",
            (classroom_id, fecha, aulas),
        )
    return {"message": "Evaluacion creada exitosamente", "status": 201}


def existe_classroom(classroom_id: int) -> bool:
    with cursor_db() as cur:
        cur.execute(
            "SELECT 1 FROM classrooms WHERE id = %s LIMIT 1",
            (classroom_id,),
        )
        return cur.fetchone() is not None
