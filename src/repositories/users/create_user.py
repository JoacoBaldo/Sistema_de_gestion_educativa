import pymysql

from src.providers.db.connection import get_connection


def create_UserRepository(user: dict) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user["username"], user["email"], user["password"]))
            conn.commit()
            return {"message": "User created successfully"}
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return {"error": "User with this email already exists"}
    finally:
        conn.close()
