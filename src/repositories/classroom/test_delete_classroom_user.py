from unittest.mock import MagicMock

from src.core.usecase.classroom.delete_classroom_user import (
    DELETE_SUCCESS_RESPONSE,
    DeleteClassroomUserUseCase,
)
from src.core.usecase.classroom.errors import (
    NOT_ADMIN_IN_CLASSROOM_ERROR,
    USER_NOT_IN_CLASSROOM_ERROR,
)


def _make_usecase(is_admin: bool, in_classroom: bool) -> DeleteClassroomUserUseCase:
    repo = MagicMock()
    repo.requester_is_admin.return_value = is_admin
    repo.user_in_classroom.return_value = in_classroom
    return DeleteClassroomUserUseCase(repository=repo)


def test_deletes_user_when_requester_is_admin():
    usecase = _make_usecase(is_admin=True, in_classroom=True)
    result, error = usecase.execute(classroom_id=1, user_id=5, requester_id=99)

    assert error is None
    assert result == DELETE_SUCCESS_RESPONSE


def test_returns_error_when_requester_is_not_admin():
    usecase = _make_usecase(is_admin=False, in_classroom=True)
    result, error = usecase.execute(classroom_id=1, user_id=5, requester_id=99)

    assert result is None
    assert error == NOT_ADMIN_IN_CLASSROOM_ERROR


def test_returns_error_when_user_not_in_classroom():
    usecase = _make_usecase(is_admin=True, in_classroom=False)
    result, error = usecase.execute(classroom_id=1, user_id=5, requester_id=99)

    assert result is None
    assert error == USER_NOT_IN_CLASSROOM_ERROR


def test_user_in_classroom_not_checked_when_requester_not_admin():
    repo = MagicMock()
    repo.requester_is_admin.return_value = False
    usecase = DeleteClassroomUserUseCase(repository=repo)

    usecase.execute(classroom_id=1, user_id=5, requester_id=99)

    repo.user_in_classroom.assert_not_called()


def test_delete_not_called_when_user_not_in_classroom():
    repo = MagicMock()
    repo.requester_is_admin.return_value = True
    repo.user_in_classroom.return_value = False
    usecase = DeleteClassroomUserUseCase(repository=repo)

    usecase.execute(classroom_id=1, user_id=5, requester_id=99)

    repo.delete_user.assert_not_called()


def test_delete_called_with_correct_args():
    repo = MagicMock()
    repo.requester_is_admin.return_value = True
    repo.user_in_classroom.return_value = True
    usecase = DeleteClassroomUserUseCase(repository=repo)

    usecase.execute(classroom_id=3, user_id=7, requester_id=99)

    repo.delete_user.assert_called_once_with(3, 7)
