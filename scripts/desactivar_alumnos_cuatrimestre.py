"""
Desactiva los alumnos de classrooms cuyos periodos académicos ya finalizaron.

Uso:
    python scripts/desactivar_alumnos_cuatrimestre.py

Lógica:
    1. Busca classrooms asociados a academic_periods con period_end < hoy.
    2. En esos classrooms, pone status_type_id = 2 a todos los alumnos activos (role_id=3).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.db.classroom import (
    desactivar_alumnos_de_classrooms,
    obtener_classroom_ids_de_periodos_finalizados,
)


def main() -> None:
    classroom_ids = obtener_classroom_ids_de_periodos_finalizados()

    if not classroom_ids:
        print("No hay periodos académicos finalizados con classrooms asociados.")
        return

    print(f"Classrooms con periodo finalizado: {classroom_ids}")

    alumnos_afectados = desactivar_alumnos_de_classrooms(classroom_ids)

    print(
        f"Se desactivaron {alumnos_afectados} alumno(s) "
        f"en {len(classroom_ids)} classroom(s)."
    )


if __name__ == "__main__":
    main()
