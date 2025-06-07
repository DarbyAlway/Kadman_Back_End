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

@waiting_vendors_bp.route("/add_selected_waiting_vendors", methods=["POST"])
def add_selected_waiting_vendors():
    try:
        data = request.json  # Expecting: {"line_ids": ["id1", "id2", ...]}
        line_ids = data.get("line_ids", [])
        
        if not line_ids:
            return jsonify({"error": "No line_ids provided"}), 400

        cursor = con.cursor()

        for line_id in line_ids:
            # Get vendor from waiting_vendors
            cursor.execute("SELECT LineID, UserProfile FROM waiting_vendors WHERE LineID = %s", (line_id,))
            row = cursor.fetchone()
            if row:
                # Insert into vendors table
                cursor.execute(
                    "INSERT INTO vendors (LineID, UserProfile) VALUES (%s, %s)",
                    (row[0], row[1])
                )
                # Delete from waiting_vendors
                cursor.execute("DELETE FROM waiting_vendors WHERE LineID = %s", (line_id,))

        con.commit()
        cursor.close()

        return jsonify({"message": "Selected waiting vendors moved to vendors table"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
