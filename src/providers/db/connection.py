import pymysql

DB_HOST = "shuttle.proxy.rlwy.net"
DB_USER = "root"
DB_PASSWORD = "WfPcTFLVDMzHgPVvzYoaWVpFJSyLutkb"
DB_PORT = 37044
DB_NAME = "railway"


def get_connection():
    return pymysql.connect(
        host=DB_HOST, user=DB_USER, password=DB_PASSWORD, database=DB_NAME, port=DB_PORT
    )
