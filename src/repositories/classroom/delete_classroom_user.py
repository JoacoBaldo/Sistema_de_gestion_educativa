import os

from sqlalchemy import create_engine, text

ADMIN_ROLE_ID = 1

REQUESTER_IS_ADMIN_QUERY = text("""
    SELECT 1 FROM classroom_users
      WHERE classroom_id = :classroom_id AND user_id = :user_id AND role_id = :role_id
    UNION
    SELECT 1 FROM classrooms
      WHERE id = :classroom_id AND user_id = :user_id
    LIMIT 1
""")

USER_IN_CLASSROOM_QUERY = text("""
    SELECT 1 FROM classroom_users
      WHERE classroom_id = :classroom_id AND user_id = :user_id
    LIMIT 1
""")

DELETE_CLASSROOM_USER_QUERY = text("""
    DELETE FROM classroom_users
      WHERE classroom_id = :classroom_id AND user_id = :user_id
""")


class DeleteClassroomUserRepository:
    def __init__(self) -> None:
        url = os.getenv("DATABASE_URL", "").replace("mysql://", "mysql+pymysql://", 1)
        self._engine = create_engine(url)

    def requester_is_admin(self, classroom_id: int, requester_id: int) -> bool:
        with self._engine.connect() as conn:
            result = conn.execute(
                REQUESTER_IS_ADMIN_QUERY,
                {
                    "classroom_id": classroom_id,
                    "user_id": requester_id,
                    "role_id": ADMIN_ROLE_ID,
                },
            ).fetchone()
        return result is not None

    def user_in_classroom(self, classroom_id: int, user_id: int) -> bool:
        with self._engine.connect() as conn:
            result = conn.execute(
                USER_IN_CLASSROOM_QUERY,
                {"classroom_id": classroom_id, "user_id": user_id},
            ).fetchone()
        return result is not None

    def delete_user(self, classroom_id: int, user_id: int) -> None:
        with self._engine.connect() as conn:
            conn.execute(
                DELETE_CLASSROOM_USER_QUERY,
                {"classroom_id": classroom_id, "user_id": user_id},
            )
            conn.commit()
