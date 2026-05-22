from src.repositories.classroom.list_classroom_teachers import (
    ClassroomTeachersRepository,
)
from src.core.usecase.classroom.list_classroom_teachers import (
    ListClassroomTeachersUseCase,
)
from src.repositories.classroom.delete_classroom_user import (
    DeleteClassroomUserRepository,
)
from src.core.usecase.classroom.delete_classroom_user import (
    DeleteClassroomUserUseCase,
)

_classroom_teachers_repo = ClassroomTeachersRepository()
_delete_classroom_user_repo = DeleteClassroomUserRepository()


def get_list_classroom_teachers_usecase() -> ListClassroomTeachersUseCase:
    return ListClassroomTeachersUseCase(repository=_classroom_teachers_repo)


def get_delete_classroom_user_usecase() -> DeleteClassroomUserUseCase:
    return DeleteClassroomUserUseCase(repository=_delete_classroom_user_repo)
