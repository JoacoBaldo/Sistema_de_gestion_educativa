from src.db import resources as db_resources
from src.db import classroom as db_classroom


def listar_recursos(classroom_id: int, usuario_id: int) -> tuple:
    if not db_classroom.puede_administrar_classroom(classroom_id, usuario_id):
        pass
    recursos = db_resources.obtener_recursos_por_aula(classroom_id)
    return recursos, None
