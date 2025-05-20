import mysql.connector
import json

# Connect to your AWS Aurora (MySQL-compatible)
conn = mysql.connector.connect(
    host="kadman-aurora-db-instance-1.clq6qs624meb.ap-southeast-2.rds.amazonaws.com",
    user="admin",
    password="12345678",
    database="kadmandb",
    port=3306
)

cursor = conn.cursor() 

# Query vendor data
cursor.execute("SELECT vendorID, shop_name, badges FROM vendors")
rows = cursor.fetchall()

# Optional: map to list of dicts
vendors = []

with open("vendors.json", "w", encoding="utf-8") as f:
    json.dump(vendors, f, ensure_ascii=False, indent=4)

# Close connection
cursor.close()
conn.close()