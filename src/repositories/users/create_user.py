import pymysql

from src.core.entities.users.users import User
from src.error import (
    format_error_response,
    DATABASE_INTEGRITY_ERROR,
    UNABLE_TO_CREATE_USER,
    USER_EMAIL_ALREADY_EXISTS,
)
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
            return format_error_response(USER_EMAIL_ALREADY_EXISTS)
        return format_error_response(DATABASE_INTEGRITY_ERROR)
    except pymysql.MySQLError:
        return format_error_response(UNABLE_TO_CREATE_USER)
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
