from src.core.entities.classroom.teacher import Teacher


def list_classroom_teachers_response(teacher: Teacher) -> dict:
    return {
        "id": teacher["id"],
        "username": teacher["username"],
        "email": teacher["email"],
        "joined_at": teacher["joined_at"].isoformat(),
    }
