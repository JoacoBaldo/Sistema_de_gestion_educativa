import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()


def obtener_conexion():
    url = os.getenv("DATABASE_URL", "")
    return create_engine(url)
