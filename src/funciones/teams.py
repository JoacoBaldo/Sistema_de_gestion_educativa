from typing import List, Optional

from src.db import classroom as db_classroom
from src.db import evaluations as db_evaluations
from src.db import teams as db_teams

from .errores import (
    EQUIPO_NO_CREADO,
    EQUIPO_NO_EXISTE,
    EVALUACION_NO_EXISTE,
    MIEMBROS_INVALIDOS,
    MIEMBROS_REQUERIDO,
    NAME_VACIO,
    NO_ES_ADMIN,
)


def _parsear_ids_miembros(miembros: List[str]) -> tuple[list[int] | None, dict | None]:
    member_ids = []
    for miembro in miembros:
        try:
            member_ids.append(int(miembro))
        except (TypeError, ValueError):
            return None, MIEMBROS_INVALIDOS
    return member_ids, None


def obtener_equipos_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        from .errores import SIN_ACCESO

        return None, SIN_ACCESO

    equipos = db_teams.listar_equipos_classroom(classroom_id)
    return equipos, None


def crear_equipo(
    nombre: str,
    miembros: List[str],
    classroom_id: int,
    usuario_id: int,
    evaluation_id: int,
) -> tuple:
    if not nombre or not nombre.strip():
        return None, NAME_VACIO

    if not miembros:
        return None, MIEMBROS_REQUERIDO

    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    if not db_evaluations.existe_evaluacion_en_classroom(evaluation_id, classroom_id):
        return None, EVALUACION_NO_EXISTE

    member_ids, error = _parsear_ids_miembros(miembros)
    if error or member_ids is None:
        return None, error or MIEMBROS_INVALIDOS

    if not db_teams.miembros_pertenecen_aula(classroom_id, member_ids):
        return None, MIEMBROS_INVALIDOS

    equipo_id = db_teams.crear_equipo_con_miembros(
        nombre.strip(),
        miembros,
        classroom_id,
    )

    if equipo_id is None:
        return None, EQUIPO_NO_CREADO

    db_teams.reemplazar_miembros(equipo_id, member_ids)
    db_teams.crear_grades_equipo(evaluation_id, equipo_id, member_ids)
    return {"message": "Team created", "id": equipo_id}, None


def editar_equipo(
    team_id: int,
    nombre: Optional[str],
    member_ids: Optional[List[int]],
    usuario_id: int,
    evaluation_id: Optional[int] = None,
) -> tuple:
    equipo = db_teams.obtener_equipo(team_id)
    if equipo is None:
        return None, EQUIPO_NO_EXISTE

    classroom_id = equipo["classroom_id"]
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    if nombre is not None:
        db_teams.actualizar_nombre(team_id, nombre.strip())

    if member_ids is not None:
        if not db_teams.miembros_pertenecen_aula(classroom_id, member_ids):
            return None, MIEMBROS_INVALIDOS
        db_teams.reemplazar_miembros(team_id, member_ids)

    if evaluation_id is not None:
        if not db_evaluations.existe_evaluacion_en_classroom(
            evaluation_id, classroom_id
        ):
            return None, EVALUACION_NO_EXISTE
        miembros_actuales = db_teams.obtener_ids_miembros(team_id)
        db_teams.crear_grades_equipo(evaluation_id, team_id, miembros_actuales)

    return {"message": "Team updated", "id": team_id}, None


def eliminar_equipo(team_id: int, usuario_id: int) -> tuple:
    equipo = db_teams.obtener_equipo(team_id)
    if equipo is None:
        return None, EQUIPO_NO_EXISTE

    if not db_classroom.puede_administrar_classroom(equipo["classroom_id"], usuario_id):
        return None, NO_ES_ADMIN

    db_teams.eliminar_equipo_completo(team_id)
    return {"message": "Team deleted", "id": team_id}, None
