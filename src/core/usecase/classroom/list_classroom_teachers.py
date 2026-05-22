from src.core.contracts.response.classroom.list_classroom_teachers_response import (
    list_classroom_teachers_response,
)
from src.core.usecase.classroom.errors import UNAUTHORIZED_CLASSROOM_ACCESS_ERROR


class ListClassroomTeachersUseCase:
    def __init__(self, repository) -> None:
        self._repository = repository

    def execute(self, classroom_id: int, requester_id: int) -> tuple[list[dict], None] | tuple[None, dict]:
        if not self._repository.user_has_access(classroom_id, requester_id):
            return None, UNAUTHORIZED_CLASSROOM_ACCESS_ERROR

        teachers = self._repository.list_teachers(classroom_id)
        return [list_classroom_teachers_response(t) for t in teachers], None
