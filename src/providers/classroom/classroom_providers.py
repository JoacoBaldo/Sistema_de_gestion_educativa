from src.repositories.classroom.list_classroom_teachers import (
    ClassroomTeachersRepository,
)
from src.core.usecase.classroom.list_classroom_teachers import (
    ListClassroomTeachersUseCase,
)

_classroom_teachers_repo = ClassroomTeachersRepository()


def get_list_classroom_teachers_usecase() -> ListClassroomTeachersUseCase:
    return ListClassroomTeachersUseCase(repository=_classroom_teachers_repo)
