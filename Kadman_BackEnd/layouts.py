from flask import Blueprint, jsonify, request,current_app,Response
import json 
from mysql.connector import Error
from db import get_db_connection
import requests
from dotenv import load_dotenv
import os

load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_Key')
layouts_bp = Blueprint('layouts', __name__) 

@layouts_bp.route("/show_all_layouts", methods=["GET"])
def show_all_layouts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM layouts")
        rows = cursor.fetchall()
        layouts = []
        for row in rows:
            layout = {
                "id": row[0],
                "name": row[1],
                "data": json.loads(row[2])
            }
            layouts.append(layout)
        cursor.close()
        return Response(
            json.dumps(layouts, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/update_layout/<int:id>", methods=["PUT"])
def update_layout(id):
    conn = get_db_connection()
    try:
        data = request.get_json()

        layout_name = data.get("name")
        layout_data = data.get("data")

        if layout_name is None or layout_data is None:
            return jsonify({"error": "Missing 'name' or 'data'"}), 400

        # Convert layout_data to JSON string
        layout_data_str = json.dumps(layout_data, ensure_ascii=False)

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE layouts SET name = %s, data = %s WHERE id = %s",
            (layout_name, layout_data_str, id)
        )
        conn.commit()
        cursor.close()

        return jsonify({"message": "Layout updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/insert_layout", methods=["POST"])
def insert_layout():
    conn = get_db_connection()
    try:
        data = request.get_json()

        layout_name = data.get("name")
        layout_data = data.get("data")

        # Add key 'status' into the json data 
        for _ , vendor_info in layout_data.items():
            vendor_info['status'] = ""

        # Convert layout_data to JSON string
        layout_data_str = json.dumps(layout_data, ensure_ascii=False)

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO layouts (name, data) VALUES (%s, %s)",
            (layout_name, layout_data_str)
        )
        conn.commit()
        new_layout_id = cursor.lastrowid # Get the ID of the newly inserted row
        cursor.close()

        return jsonify({"message": "Layout added successfully", "id": new_layout_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/delete_layout/<int:id>", methods=["DELETE"])
def delete_layout(id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # First, check if the layout exists
        cursor.execute("SELECT id FROM layouts WHERE id = %s", (id,))
        existing_layout = cursor.fetchone()

        if not existing_layout:
            cursor.close()
            return jsonify({"error": f"Layout with ID {id} not found"}), 404

        # If it exists, proceed with deletion
        cursor.execute("DELETE FROM layouts WHERE id = %s", (id,))
        conn.commit()
        cursor.close()

        return jsonify({"message": f"Layout with ID {id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Begin attendance check for every vendors
@layouts_bp.route("/begin_attendance/<int:id>", methods=["GET"])
def begin_attendance(id):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT data FROM layouts WHERE id = %s", (id,))
        row = cursor.fetchone()

        if not row:
            return jsonify({"error": f"Layout with ID {id} not found"}), 404

        layout_data = json.loads(row[0])
        results = []

        for slot, value in layout_data.items():
            if isinstance(value, dict) and "vendorID" in value:
                vendor_id = value["vendorID"]

                cursor.execute("SELECT lineID FROM vendors WHERE vendorID = %s", (vendor_id,))
                vendor_row = cursor.fetchone()

                if vendor_row and vendor_row[0]:
                    line_user_id = vendor_row[0]
                    attendance_url = f"https://2d326c2dd4bd.ngrok-free.app/check_attendance?layout_id={id}"
                    message_text = f"Please check your attendance here: {attendance_url}"

                    # Send LINE message BEFORE updating DB
                    status_code, response_text = send_line_multicast([line_user_id], message_text)

                    results.append({
                        "slot": slot,
                        "vendorID": vendor_id,
                        "lineID": line_user_id,
                        "notification_status": status_code,
                        "notification_response": response_text,
                    })
                else:
                    results.append({
                        "slot": slot,
                        "vendorID": vendor_id,
                        "lineID": None,
                        "notification_status": "skipped",
                        "notification_response": "No LINE user ID found"
                    })

        # DB updates last, using still-active connection
        change_all_status_to_pending_attendance(id, conn, cursor)
        activate_layout_status(id, conn, cursor)

        conn.commit()
        return jsonify(results), 200

    except Exception as e:
        print(f"❌ Error in begin_attendance: {e}")
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if conn is not None and conn.is_connected():
            conn.close()

def activate_layout_status(id,conn,cursor):
    try:
        # Update the status column to 'active' for the given layout id
        cursor.execute("UPDATE layouts SET status = %s WHERE id = %s", ("active", id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": f"No layout found with id={id}"}), 404

        return jsonify({"message": f"Layout id={id} status updated to 'active'."}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# make the layout status be inactive
def deactivate_layout_status(id,conn,cursor):
    try:
        cursor.execute("UPDATE layouts SET status = %s WHERE id = %s", ("inactive", id))
        conn.commit()

        if cursor.rowcount == 0:
            return jsonify({"error": f"No layout found with id={id}"}), 404

        return jsonify({"message": f"Layout id={id} status updated to 'inactive'."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def send_line_multicast(user_ids, message_text):
    url = 'https://api.line.me/v2/bot/message/multicast'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
    }
    payload = {
        "to": user_ids,
        "messages": [{"type": "text", "text": message_text}]
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text


# Change all vendor's status in layout table to 'pending' 
def change_all_status_to_pending_attendance(id,conn,cursor):
    cursor.execute("SELECT data FROM layouts WHERE id = %s", (id,))
    row = cursor.fetchone()
    if row:
        data_json = row[0]
        data = json.loads(data_json)
        for _ , vendor_info in data.items():
            vendor_info['status'] = "pending attendance"  # <-- here
        new_json_str = json.dumps(data, ensure_ascii=False)
        cursor.execute("UPDATE layouts SET data = %s WHERE id = %s", (new_json_str, 3))
        conn.commit()
        print("Updated data with 'status' set to 'pending attendance'.")

    else:
        print(f"No record with {id} found.")


# Change all vendor's status in layout table to 'pending payment' already check 
def change_all_status_to_pending_payment(id,conn,cursor):
    cursor.execute("SELECT data FROM layouts WHERE id = %s", (id,))
    row = cursor.fetchone()
    if row:
        data_json = row[0]
        data = json.loads(data_json)
        for _ , vendor_info in data.items():
            vendor_info['status'] = "pending payment"
        new_json_str = json.dumps(data, ensure_ascii=False)
        cursor.execute("UPDATE layouts SET data = %s WHERE id = %s", (new_json_str, 3))
        conn.commit()
        print("Updated data with 'status' set to 'pending payment'.")

    else:
        print(f"No record with {id} found.")

