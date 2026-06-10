import os

from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


_engine = None


def obtener_conexion():
    global _engine
    if _engine is None:
        url = os.getenv("DATABASE_URL", "")
        _engine = create_engine(url)
    return _engine
