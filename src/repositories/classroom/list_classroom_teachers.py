import os
from datetime import datetime

from sqlalchemy import create_engine, text

from src.core.entities.classroom.teacher import Teacher

PROFESSOR_ROLE_ID = 0
LIST_TEACHERS_QUERY = text("""
    SELECT u.id, u.username, u.email, cu.created_at
    FROM classroom_users cu
    JOIN users u ON cu.user_id = u.id
    WHERE cu.classroom_id = :classroom_id
      AND cu.role_id = :role_id
""")

USER_ACCESS_QUERY = text("""
    SELECT 1 FROM classroom_users
      WHERE classroom_id = :classroom_id AND user_id = :user_id
    UNION
    SELECT 1 FROM classrooms
      WHERE id = :classroom_id AND user_id = :user_id
    LIMIT 1
""")


class ClassroomTeachersRepository:
    def __init__(self) -> None:
        url = os.getenv("DATABASE_URL", "").replace("mysql://", "mysql+pymysql://", 1)
        self._engine = create_engine(url)

    def list_teachers(self, classroom_id: int) -> list[Teacher]:
        with self._engine.connect() as conn:
            rows = conn.execute(
                LIST_TEACHERS_QUERY,
                {"classroom_id": classroom_id, "role_id": PROFESSOR_ROLE_ID},
            ).fetchall()

        return [
            Teacher(
                id=row.id,
                username=row.username,
                email=row.email,
                joined_at=row.created_at
                if isinstance(row.created_at, datetime)
                else datetime.fromisoformat(str(row.created_at)),
            )
            for row in rows
        ]

    def user_has_access(self, classroom_id: int, user_id: int) -> bool:
        with self._engine.connect() as conn:
            result = conn.execute(
                USER_ACCESS_QUERY,
                {"classroom_id": classroom_id, "user_id": user_id},
            ).fetchone()

        return result is not None
