from flask import Blueprint, jsonify, request
from db import wait_for_db_connection # Import db
import json 
from flask import Response
from mysql.connector import Error

waiting_vendors_bp = Blueprint('waiting_vendors', __name__) 
conn = wait_for_db_connection()

@waiting_vendors_bp.route("/show_all_waiting_vendors", methods=["GET"])
def show_all_waiting_vendors():
    try:
        cursor = conn.cursor()
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

        cursor = conn.cursor()

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

        conn.commit()
        cursor.close()

        return jsonify({"message": "Selected waiting vendors moved to vendors table"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@waiting_vendors_bp.route("/add_to_real_vendors",methods=["POST"])
def add_to_real_vendors():
    '''
    Add to real vendors table.
    Expects JSON data with 'shopname', 'phone_number', 'badges', and 'UserProfile'.
    '''
    if not request.is_json:
        return jsonify({"message": "Request must be JSON", "success": False}), 400

    data = request.get_json()
    shopname = data.get('shopname')
    phone_number = data.get('phone_number')
    badges = data.get('badges')
    user_profile = data.get('UserProfile')

    if not all([shopname, phone_number, user_profile]):
        return jsonify({"message": "Missing required fields: shopname, phone_number, UserProfile", "success": False}), 400
    # Convert badges to a JSON string if it's not None, otherwise set to None
    # MySQL JSON type will handle conversion if passed as a Python object,
    # but explicitly converting can be safer if there are issues.
    # If the frontend sends a string, no conversion is needed.
    # If the frontend sends an object/array, json.dumps is appropriate.
    
    if badges is not None and not isinstance(badges, str):
        try:
            badges = json.dumps(badges)
        except TypeError:
            return jsonify({"message": "Invalid format for 'badges' field", "success": False}), 400
    elif badges == "": # Handle empty string for badges
        badges = None

    sql_insert_query = """
        INSERT INTO real_vendors (shopname, phone_number, badges, UserProfile)
        VALUES (%s, %s, %s, %s)
        """
    
    try:
        cursor = conn.cursor()
        sql_insert_query = """
        INSERT INTO real_vendors (shopname, phone_number, badges, UserProfile)
        VALUES (%s, %s, %s, %s)
        """

        record_tuple = (shopname, phone_number, badges, user_profile)
        cursor.execute(sql_insert_query, record_tuple)
        conn.commit()

         # Check if any rows were affected (optional but good practice)
        if cursor.rowcount > 0:
            return jsonify({
                "message": "Vendor added to real_vendors successfully",
                "success": True,
                "vendorsID": cursor.lastrowid # Get the ID of the newly inserted row
            }), 201 # 201 Created
        else:
            return jsonify({"message": "Failed to add vendor (no rows affected)", "success": False}), 500
    except Error as err:
        print(f"Error inserting data into real_vendors: {err}")
        # Rollback in case of error
        if conn:
            conn.rollback()
        return jsonify({"message": f"Database error: {err}", "success": False}), 500
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return jsonify({"message": f"An unexpected error occurred: {e}", "success": False}), 500
    finally:
        # Close cursor and connection
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
            print("MySQL connection closed.")
