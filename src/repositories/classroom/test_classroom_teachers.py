from datetime import datetime
from unittest.mock import MagicMock

from src.core.contracts.response.classroom.list_classroom_teachers_response import (
    list_classroom_teachers_response,
)
from src.core.entities.classroom.teacher import Teacher
from src.core.usecase.classroom.errors import UNAUTHORIZED_CLASSROOM_ACCESS_ERROR
from src.core.usecase.classroom.list_classroom_teachers import (
    ListClassroomTeachersUseCase,
)

FIXED_DT = datetime(2024, 3, 10, 9, 0, 0)

TEACHER_A = Teacher(id=1, username="profA", email="profA@uni.edu", joined_at=FIXED_DT)
TEACHER_B = Teacher(id=2, username="profB", email="profB@uni.edu", joined_at=FIXED_DT)


def _make_usecase(
    teachers: list[Teacher], has_access: bool
) -> ListClassroomTeachersUseCase:
    repo = MagicMock()
    repo.list_teachers.return_value = teachers
    repo.user_has_access.return_value = has_access
    return ListClassroomTeachersUseCase(repository=repo)


def test_returns_professor_list_when_user_has_access():
    usecase = _make_usecase([TEACHER_A, TEACHER_B], has_access=True)
    result, error = usecase.execute(classroom_id=1, requester_id=99)

    assert error is None
    assert len(result) == 2
    assert result[0]["id"] == TEACHER_A["id"]
    assert result[1]["id"] == TEACHER_B["id"]


def test_returns_empty_list_when_no_professors_in_classroom():
    usecase = _make_usecase([], has_access=True)
    result, error = usecase.execute(classroom_id=1, requester_id=99)

    assert error is None
    assert result == []


def test_returns_error_dict_when_user_has_no_access():
    usecase = _make_usecase([TEACHER_A], has_access=False)
    result, error = usecase.execute(classroom_id=1, requester_id=99)

    assert result is None
    assert error == UNAUTHORIZED_CLASSROOM_ACCESS_ERROR


def test_repository_not_called_when_access_denied():
    repo = MagicMock()
    repo.user_has_access.return_value = False
    usecase = ListClassroomTeachersUseCase(repository=repo)

    usecase.execute(classroom_id=1, requester_id=99)

    repo.list_teachers.assert_not_called()


def test_response_function_returns_correct_dict():
    result = list_classroom_teachers_response(TEACHER_A)

    assert result == {
        "id": TEACHER_A["id"],
        "username": TEACHER_A["username"],
        "email": TEACHER_A["email"],
        "joined_at": FIXED_DT.isoformat(),
    }


def test_use_case_maps_all_teachers_to_dicts():
    usecase = _make_usecase([TEACHER_A, TEACHER_B], has_access=True)
    result, error = usecase.execute(classroom_id=5, requester_id=10)

    assert error is None
    assert all(isinstance(r, dict) for r in result)
    assert [r["username"] for r in result] == ["profA", "profB"]
