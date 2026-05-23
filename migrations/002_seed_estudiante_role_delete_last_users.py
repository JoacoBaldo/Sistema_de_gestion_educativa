import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()

ADD_ESTUDIANTE_ROLE = text("""
    INSERT IGNORE INTO role_types (id, name)
    VALUES (3, 'Estudiante')
""")

DELETE_LAST_40_USERS = text("""
    DELETE FROM users
    WHERE id IN (
        SELECT id FROM (
            SELECT id FROM users
            ORDER BY id DESC
            LIMIT 40
        ) AS to_delete
    )
""")

CREATE_CLASSROOM = text("""INSERT INTO `classrooms` (`name`, `department`, `university`) VALUES
('Diseño de Sistemas - Curso 1', 'Computación', 'UBA - FIUBA');""")

CREATE_CLASSROOM_USERS = text("""INSERT INTO `classroom_users` (`classroom_id`, `user_id`, `role_id`,`status_type_id`) VALUES
(3, 4, 2, 1),
(3, 6, 0, 1),
(3, 7, 3, 1);""")


def run() -> None:
    url = os.getenv("DATABASE_URL", "").replace("mysql://", "mysql+pymysql://", 1)
    engine = create_engine(url)

    with engine.begin() as conn:
        # conn.execute(ADD_ESTUDIANTE_ROLE)
        # conn.execute(CREATE_CLASSROOM)
        conn.execute(CREATE_CLASSROOM_USERS)
        # result = conn.execute(DELETE_LAST_40_USERS)
        # print(f"{result.rowcount} usuario(s) eliminado(s)")


if __name__ == "__main__":
    run()
