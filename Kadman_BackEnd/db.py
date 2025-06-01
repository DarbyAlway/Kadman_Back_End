import mysql.connector
import time
def get_connection():
    return mysql.connector.connect(
        host="kadman-aurora-db-instance-1.clq6qs624meb.ap-southeast-2.rds.amazonaws.com",
        user="admin",
        password="12345678",
        database="kadmandb",
        port=3306,
        charset='utf8mb4'
    )

def wait_for_db_connection():
    while True:
        try:
            conn = get_connection()
            print("✅ Successfully connected to MySQL database")
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to DB: {e}. Retrying in 1 seconds...")
            time.sleep(1)