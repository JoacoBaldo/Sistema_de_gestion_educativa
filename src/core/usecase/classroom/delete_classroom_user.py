from src.core.usecase.classroom.errors import (
    NOT_ADMIN_IN_CLASSROOM_ERROR,
    USER_NOT_IN_CLASSROOM_ERROR,
)

DELETE_SUCCESS_RESPONSE = {"message": "User removed from classroom"}


class DeleteClassroomUserUseCase:
    def __init__(self, repository) -> None:
        self._repository = repository

    def execute(
        self, classroom_id: int, user_id: int, requester_id: int
    ) -> tuple[dict, None] | tuple[None, dict]:
        if not self._repository.requester_is_admin(classroom_id, requester_id):
            return None, NOT_ADMIN_IN_CLASSROOM_ERROR

        if not self._repository.user_in_classroom(classroom_id, user_id):
            return None, USER_NOT_IN_CLASSROOM_ERROR

        self._repository.delete_user(classroom_id, user_id)
        return DELETE_SUCCESS_RESPONSE, None
