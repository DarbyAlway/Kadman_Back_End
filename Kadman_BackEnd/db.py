import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="kadman-aurora-db-instance-1.clq6qs624meb.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="12345678",
        database="kadmandb",
        port=3306,
        charset='utf8mb4'
    )