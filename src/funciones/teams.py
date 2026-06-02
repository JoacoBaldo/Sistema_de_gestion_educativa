from typing import List, Optional

from src.db import classroom as db_classroom
from src.db import teams as db_teams
from .errores import EQUIPO_NO_EXISTE, MIEMBROS_INVALIDOS, NO_ES_ADMIN


def editar_equipo(
    team_id: int,
    nombre: Optional[str],
    member_ids: Optional[List[int]],
    usuario_id: int,
) -> tuple:
    equipo = db_teams.obtener_equipo(team_id)
    if equipo is None:
        return None, EQUIPO_NO_EXISTE

    classroom_id = equipo["classroom_id"]
    if not db_classroom.es_admin_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    if nombre is not None:
        db_teams.actualizar_nombre(team_id, nombre.strip())

    if member_ids is not None:
        if not db_teams.miembros_pertenecen_aula(classroom_id, member_ids):
            return None, MIEMBROS_INVALIDOS
        db_teams.reemplazar_miembros(team_id, member_ids)

    return {"message": "Team updated", "id": team_id}, None


def eliminar_equipo(team_id: int, usuario_id: int) -> tuple:
    equipo = db_teams.obtener_equipo(team_id)
    if equipo is None:
        return None, EQUIPO_NO_EXISTE

    if not db_classroom.es_admin_classroom(equipo["classroom_id"], usuario_id):
        return None, NO_ES_ADMIN

    db_teams.eliminar_equipo_completo(team_id)
    return {"message": "Team deleted", "id": team_id}, None
