import os
from contextlib import contextmanager
from urllib.parse import unquote, urlparse

import pymysql
import pymysql.cursors
from dotenv import load_dotenv

load_dotenv()


def _configuracion_db() -> dict:
    url = os.getenv("DATABASE_URL", "")
    if url:
        if url.startswith("mysql+pymysql://"):
            url = "mysql://" + url[len("mysql+pymysql://") :]
        elif url.startswith("mysql://"):
            pass
        else:
            url = "mysql://" + url.split("://", 1)[-1]

        parsed = urlparse(url)
        return {
            "host": parsed.hostname or "localhost",
            "port": parsed.port or 3306,
            "user": unquote(parsed.username or ""),
            "password": unquote(parsed.password or ""),
            "database": parsed.path.lstrip("/"),
        }

    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "usuario"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "gestion_educativa"),
    }


def obtener_conexion():
    config = _configuracion_db()
    return pymysql.connect(
        host=config["host"],
        port=config["port"],
        user=config["user"],
        password=config["password"],
        database=config["database"],
        charset="utf8mb4",
        autocommit=False,
        cursorclass=pymysql.cursors.DictCursor,
    )


@contextmanager
def cursor_db(*, commit: bool = False):
    conn = obtener_conexion()
    cursor = conn.cursor()
    try:
        yield cursor
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
