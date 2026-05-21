import pymysql

from src.core.entities.users.users import User
from src.providers.db.connection import get_connection


def create_UserRepository(user: User) -> dict:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
            cursor.execute(sql, (user["username"], user["email"], user["password"]))
            conn.commit()
            return {"message": "User created successfully", "status_code": 201}
    except pymysql.err.IntegrityError as e:
        if e.args[0] == 1062:
            return {"error": "User with this email already exists", "status_code": 409}
        return {"error": "Database integrity error", "status_code": 500}
    except pymysql.MySQLError:
        return {"error": "Unable to create user", "status_code": 500}
    finally:
        conn.close()


def email_exists(email: str) -> bool:
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            sql = "SELECT 1 FROM users WHERE email = %s LIMIT 1"
            cursor.execute(sql, (email,))
            result = cursor.fetchone()
            return result is not None
    finally:
        conn.close()
