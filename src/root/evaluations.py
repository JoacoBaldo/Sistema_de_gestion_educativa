from flask import Blueprint, jsonify, request

import csv
import io

from src.funciones.auth import verificar_token
from src.funciones.evaluations import (
    actualizar_nota_estudiante,
    cargar_notas_masivas_logic,
    eliminar_nota_estudiante,
    obtener_evaluaciones,
    actualizar_evaluacion,
    crear_evaluacion,
    eliminar_evaluacion,
    crear_nota_individual_o_grupal,
)


from .utils import extraer_token, responder_error

evaluacion_bp = Blueprint("evaluacion", __name__)


@evaluacion_bp.route(
    "/api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["GET"]
)
def listar_evaluaciones_aula(classroom_id):
    token = extraer_token()
    usuario, error_token = verificar_token(token)
    if error_token:
        return responder_error(error_token)

    evaluaciones, error = obtener_evaluaciones(classroom_id)

    if error:
        return responder_error(error)

    return jsonify(evaluaciones), 200


@evaluacion_bp.route(
    "/api/v1/classroom/<int:classroom_id>/evaluaciones", methods=["POST"]
)
def crear_evaluacion_root(classroom_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    if request.is_json:
        body = request.get_json(silent=True) or {}
    else:
        body = request.form or {}

    name = body.get("name") or body.get("nombre")
    if not isinstance(name, str):
        name = ""

    due_date = body.get("due_date")
    if not isinstance(due_date, str):
        due_date = None

    evaluation_type_raw = body.get("evaluation_type_id") or body.get("tipo")
    try:
        evaluation_type_id = (
            int(evaluation_type_raw) if evaluation_type_raw is not None else 0
        )
    except (TypeError, ValueError):
        evaluation_type_id = 0

    referenced_eval_raw = body.get("referenced_eval_id")
    try:
        referenced_eval_id = (
            int(referenced_eval_raw) if referenced_eval_raw is not None else None
        )
    except (TypeError, ValueError):
        referenced_eval_id = None

    individual_raw = body.get("individual", 1)
    try:
        individual = int(individual_raw)
    except (TypeError, ValueError):
        individual = 1

    if not isinstance(evaluation_type_id, int) or evaluation_type_id == 0:
        return responder_error({"mensaje": "evaluation_type_id requerido"})

    resultado, error = crear_evaluacion(
        classroom_id, name, evaluation_type_id, referenced_eval_id, individual, due_date
    )
    if error:
        return responder_error(error)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route("/api/v1/evaluaciones/<int:evaluation_id>", methods=["PATCH"])
def actualizar_evaluacion_root(evaluation_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) if request.is_json else request.form or {}

    classroom_id = body.get("classroom_id")
    name = body.get("name") or body.get("nombre")

    evaluation_type_raw = body.get("evaluation_type_id") or body.get("tipo")
    try:
        evaluation_type_id = (
            int(evaluation_type_raw) if evaluation_type_raw is not None else None
        )
    except (TypeError, ValueError):
        evaluation_type_id = None

    referenced_eval_id = body.get("referenced_eval_id")
    individual = body.get("individual")
    due_date = body.get("due_date")

    resultado, error = actualizar_evaluacion(
        classroom_id,
        name,
        evaluation_type_id,
        referenced_eval_id,
        individual,
        due_date,
        evaluation_id,
    )
    if error:
        return responder_error(error)
    return jsonify(resultado), 200


@evaluacion_bp.route("/api/v1/evaluaciones/<int:evaluation_id>", methods=["DELETE"])
def eliminar_evaluacion_root(evaluation_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error_del = eliminar_evaluacion(evaluation_id)
    if error_del:
        return responder_error(error_del)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route(
    "/api/v1/evaluations/<int:evaluation_id>/bulk-grades", methods=["POST"]
)
def api_bulk_grades(evaluation_id):
    token = extraer_token()
    usuario, error = verificar_token(token)
    if error:
        return responder_error(error)

    if "file_csv" in request.files:
        file = request.files["file_csv"]
        stream = io.StringIO(file.stream.read().decode("utf-8"), newline="")
        reader = csv.DictReader(stream)

        grades = []
        for row in reader:
            tipo = "equipo" if "equipo" in row else "documento"
            identificador = (
                row.get("equipo") or row.get("documento") or row.get("email")
            )

            grades.append(
                {"identifier": identificador, "score": float(row["nota"]), "type": tipo}
            )

        classroom_id = request.form.get("classroom_id")
    else:
        body = request.get_json(silent=True) or {}
        classroom_id = body.get("classroom_id")
        grades = body.get("grades", [])

    if not classroom_id:
        return responder_error(
            {"error": "El classroom_id es requerido.", "status": 400}
        )

    resultado, err = cargar_notas_masivas_logic(
        int(classroom_id), evaluation_id, grades
    )

    if err:
        return responder_error(err)
    return jsonify(resultado), 200


@evaluacion_bp.route(
    "/api/v1/evaluations/<int:evaluation_id>/grades/<int:user_id>", methods=["PUT"]
)
def api_actualizar_nota(evaluation_id: int, user_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    body = request.get_json(silent=True) or {}
    score = body.get("score")

    resultado, error_logica = actualizar_nota_estudiante(evaluation_id, user_id, score)
    if error_logica:
        return responder_error(error_logica)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route(
    "/api/v1/evaluations/<int:evaluation_id>/grades/<int:user_id>", methods=["DELETE"]
)
def api_eliminar_nota(evaluation_id: int, user_id: int):
    token = extraer_token()
    _, error = verificar_token(token)
    if error:
        return responder_error(error)

    resultado, error_logica = eliminar_nota_estudiante(evaluation_id, user_id)
    if error_logica:
        return responder_error(error_logica)

    return jsonify(resultado), resultado["status"]


@evaluacion_bp.route("/api/v1/evaluations/<int:evaluation_id>/grades", methods=["POST"])
def cargar_nota_manual_tradicional(evaluation_id: int):
    data = request.get_json() or {}

    score_raw = data.get("score")
    user_id_raw = data.get("user_id")
    team_id_raw = data.get("team_id")

    try:
        score = float(score_raw) if score_raw is not None else None
        user_id = int(user_id_raw) if user_id_raw else None
        team_id = int(team_id_raw) if team_id_raw else None

        if score is None or (score < 1 or score > 10):
            return jsonify(
                {"error": "La nota debe ser un número válido entre 1 y 10."}
            ), 400

        resultado, error_logica = crear_nota_individual_o_grupal(
            evaluation_id=evaluation_id, score=score, user_id=user_id, team_id=team_id
        )

        if error_logica:
            msg = error_logica.get("error", "Ocurrió un error al procesar la nota.")
            return jsonify({"error": msg}), 400

        return jsonify(
            {"message": "¡Calificación registrada con éxito!", "data": resultado}
        ), 200

    except ValueError:
        return jsonify(
            {
                "error": "Los identificadores de estudiante o equipo no tienen un formato válido."
            }
        ), 400
    except Exception as e:
        return jsonify({"error": f"Error interno del servidor: {str(e)}"}), 500
