from collections import defaultdict
from src.db import classroom as db_classroom
from src.db import metrics as db_metrics
from .errores import CLASSROOM_NO_EXISTE, NO_ES_ADMIN, SIN_ACCESO


def obtener_metricas_classroom(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.existe_classroom(classroom_id):
        return None, CLASSROOM_NO_EXISTE

    if not db_classroom.usuario_en_classroom(classroom_id, usuario_id):
        return None, SIN_ACCESO

    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        return None, NO_ES_ADMIN

    # Obtener scores y calcular promedio de aprobados
    scores_raw = db_metrics.obtener_promedio_aprobados(classroom_id)
    promedio_aprobados = _calcular_promedio_aprobados(scores_raw)

    # Obtener fechas de ingreso y agrupar por año
    ingresos_raw = db_metrics.obtener_ingresos_por_año(classroom_id)
    ingresos_por_año = _agrupar_ingresos_por_año(ingresos_raw)

    conteos = db_metrics.obtener_conteos_estudiantes(classroom_id)

    return {
        "promedio_aprobados": round(promedio_aprobados * 100, 2)
        if promedio_aprobados is not None
        else 0,
        "ingresos_por_año": ingresos_por_año,
        "total_estudiantes": conteos["total_estudiantes"],
        "total_activos": conteos["total_activos"],
        "total_abandonaron": conteos["total_abandonaron"],
    }, None


def _calcular_promedio_aprobados(scores_data: list[dict]) -> float | None:
    """Calcula el porcentaje de estudiantes que aprobaron (promedio >= 4)"""
    if not scores_data:
        return None

    # Agrupar scores por user_id
    user_scores = defaultdict(list)
    for item in scores_data:
        user_scores[item["user_id"]].append(item["score"])

    # Calcular promedio por usuario y contar aprobados
    aprobados = 0
    for user_id, scores in user_scores.items():
        promedio_usuario = sum(scores) / len(scores)
        if promedio_usuario >= 4:
            aprobados += 1

    return aprobados / len(user_scores) if user_scores else None


def _agrupar_ingresos_por_año(ingresos_data: list[dict]) -> list[dict]:
    """Agrupa ingresos por año a partir de las fechas"""
    ingresos_por_año = defaultdict(int)

    for item in ingresos_data:
        año = item["created_at"].year
        ingresos_por_año[año] += 1

    # Retornar ordenado por año
    return [
        {"year": año, "total": total} for año, total in sorted(ingresos_por_año.items())
    ]
