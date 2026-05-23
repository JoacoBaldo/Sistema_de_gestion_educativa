import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def obtener_conexion():
    url = os.getenv("DATABASE_URL", "")
    engine = create_engine(url)
    return engine
