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

    promedio_aprobados = db_metrics.obtener_promedio_aprobados(classroom_id)
    ingresos_por_anio = db_metrics.obtener_ingresos_por_anio(classroom_id)
    conteos = db_metrics.obtener_conteos_estudiantes(classroom_id)

    return {
        "promedio_aprobados": round(promedio_aprobados * 100, 2) if promedio_aprobados is not None else 0,
        "ingresos_por_anio": ingresos_por_anio,
        "total_estudiantes": conteos["total_estudiantes"],
        "total_activos": conteos["total_activos"],
        "total_abandonaron": conteos["total_abandonaron"],
    }, None
