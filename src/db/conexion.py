import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


_engine = None


def obtener_conexion():
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "")
        if not url:
            raise ValueError(
                "DATABASE_URL no está configurada. Verifica las variables de entorno en Railway."
            )
        try:
            _engine = create_engine(
                url,
                pool_size=20,
                max_overflow=10,
                pool_pre_ping=True,
                pool_recycle=3600,
            )
        except Exception as e:
            raise RuntimeError(f"Error al conectar a la base de datos: {str(e)}")
    return _engine
