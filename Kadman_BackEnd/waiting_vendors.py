from flask import Blueprint, jsonify, request
from db import wait_for_db_connection # Import db
import json 
from flask import Response

waiting_vendors_bp = Blueprint('waiting_vendors', __name__) 
con = wait_for_db_connection()

@waiting_vendors_bp.route("/show_all_waiting_vendors", methods=["GET"])
def show_all_waiting_vendors():
    try:
        cursor = con.cursor()
        cursor.execute("SELECT * FROM waiting_vendors")
        rows = cursor.fetchall()
        vendors = []
        for row in rows:
            vendor = {
                "LineID": row[0],
                "UserProfile": row[1]
            }
            vendors.append(vendor)
        cursor.close()
        return jsonify(vendors), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
