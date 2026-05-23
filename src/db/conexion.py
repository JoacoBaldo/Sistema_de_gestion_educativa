import os
from sqlalchemy import create_engine

def obtener_conexion():
    database_url = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://usuario:contraseña@localhost/gestion_educativa"
    )
    engine = create_engine(database_url)
    return engine
