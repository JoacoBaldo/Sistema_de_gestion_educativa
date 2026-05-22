from flask import Blueprint

from src.entrypoints.classroom.classroom import list_classroom_professors
from src.entrypoints.classroom.delete_classroom_user import delete_classroom_user

classroom_bp = Blueprint("classroom", __name__)

classroom_bp.add_url_rule(
    "/api/v1/classrooms/<int:classroom_id>/professors",
    view_func=list_classroom_professors,
    methods=["GET"],
)

classroom_bp.add_url_rule(
    "/api/v1/classrooms/<int:classroom_id>/user/<int:user_id>",
    view_func=delete_classroom_user,
    methods=["DELETE"],
)
