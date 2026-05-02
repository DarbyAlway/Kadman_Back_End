import json
import os
import requests
from flask import Blueprint, jsonify, request, Response
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

layouts_bp = Blueprint('layouts', __name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_Key')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')


@layouts_bp.route("/show_all_layouts", methods=["GET"])
def show_all_layouts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM layouts")
        rows = cursor.fetchall()
        layouts = [
            {"id": row[0], "name": row[1], "data": json.loads(row[2])}
            for row in rows
        ]
        cursor.close()
        return Response(json.dumps(layouts, ensure_ascii=False), content_type="application/json")
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

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE layouts SET name = %s, data = %s WHERE id = %s",
            (layout_name, json.dumps(layout_data, ensure_ascii=False), id)
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

        for vendor_info in layout_data.values():
            vendor_info['status'] = ""

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO layouts (name, data) VALUES (%s, %s)",
            (layout_name, json.dumps(layout_data, ensure_ascii=False))
        )
        conn.commit()
        new_layout_id = cursor.lastrowid
        cursor.close()
        return jsonify({"message": "Layout added successfully", "id": new_layout_id}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@layouts_bp.route("/delete_layout/<int:id>", methods=["DELETE"])
def delete_layout(id):
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM layouts WHERE id = %s", (id,))
        if not cursor.fetchone():
            cursor.close()
            return jsonify({"error": f"Layout with ID {id} not found"}), 404

        cursor.execute("DELETE FROM layouts WHERE id = %s", (id,))
        conn.commit()
        cursor.close()
        return jsonify({"message": f"Layout {id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


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
            return jsonify({"error": f"Layout {id} not found"}), 404

        layout_data = json.loads(row[0])
        results = []

        for slot, value in layout_data.items():
            if not isinstance(value, dict) or "vendorID" not in value:
                continue

            vendor_id = value["vendorID"]
            cursor.execute("SELECT lineID FROM vendors WHERE vendorID = %s", (vendor_id,))
            vendor_row = cursor.fetchone()

            if vendor_row and vendor_row[0]:
                line_user_id = vendor_row[0]
                status_code, response_text = send_line_multicast(
                    [line_user_id],
                    f"Please check your attendance here: {FRONTEND_URL}/?layout_id={id}"
                )
                results.append({
                    "slot": slot, "vendorID": vendor_id, "lineID": line_user_id,
                    "notification_status": status_code, "notification_response": response_text,
                })
            else:
                results.append({
                    "slot": slot, "vendorID": vendor_id, "lineID": None,
                    "notification_status": "skipped", "notification_response": "No LINE user ID found",
                })

        _change_all_status(id, conn, cursor, "pending attendance")
        _set_layout_status(id, conn, cursor, "active")
        conn.commit()
        return jsonify(results), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@layouts_bp.route("/get_all_active_layout", methods=["GET"])
def get_all_active_layout():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, status, data FROM layouts WHERE status = %s", ("active",))
        layouts = [
            {"id": r[0], "name": r[1], "status": r[2], "data": json.loads(r[3]) if r[3] else {}}
            for r in cursor.fetchall()
        ]
        cursor.close()
        conn.close()
        return jsonify(layouts), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@layouts_bp.route("/reset_all_attendance", methods=["PUT"])
def reset_all_attendance():
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, data FROM layouts")

        for layout_id, data_json in cursor.fetchall():
            if not data_json:
                continue
            data = json.loads(data_json)
            for vendor_info in data.values():
                if isinstance(vendor_info, dict) and "status" in vendor_info:
                    vendor_info["status"] = ""
            cursor.execute(
                "UPDATE layouts SET data = %s, status = %s WHERE id = %s",
                (json.dumps(data, ensure_ascii=False), "inactive", layout_id)
            )

        conn.commit()
        return jsonify({"message": "All layouts reset to inactive"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()


@layouts_bp.route("/send_notification/<int:id>", methods=["GET"])
def send_notification(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT data FROM layouts WHERE id = %s", (id,))
        row = cursor.fetchone()
        if not row:
            return jsonify({"error": f"Layout {id} not found"}), 404

        layout_data = json.loads(row[0])
        results = []
        for slot, value in layout_data.items():
            if isinstance(value, dict) and "vendorID" in value:
                cursor.execute("SELECT lineID FROM vendors WHERE vendorID = %s", (value["vendorID"],))
                vendor_row = cursor.fetchone()
                if vendor_row and vendor_row[0]:
                    status_code, _ = send_line_multicast([vendor_row[0]], f"Notification for layout {id}")
                    results.append({"slot": slot, "status": status_code})

        cursor.close()
        conn.close()
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Internal helpers ---

def _set_layout_status(id, conn, cursor, status):
    cursor.execute("UPDATE layouts SET status = %s WHERE id = %s", (status, id))
    conn.commit()


def _change_all_status(id, conn, cursor, status):
    cursor.execute("SELECT data FROM layouts WHERE id = %s", (id,))
    row = cursor.fetchone()
    if not row:
        return
    data = json.loads(row[0])
    for vendor_info in data.values():
        if isinstance(vendor_info, dict):
            vendor_info['status'] = status
    cursor.execute(
        "UPDATE layouts SET data = %s WHERE id = %s",
        (json.dumps(data, ensure_ascii=False), id)
    )
    conn.commit()


def send_line_multicast(user_ids, message_text):
    response = requests.post(
        'https://api.line.me/v2/bot/message/multicast',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'},
        json={"to": user_ids, "messages": [{"type": "text", "text": message_text}]}
    )
    return response.status_code, response.text


def send_line_qrcode(user_ids, amount):
    promptpay_link = f"https://promptpay.io/0864395473/{amount}00"
    qrcode_url = f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={promptpay_link}"
    response = requests.post(
        'https://api.line.me/v2/bot/message/multicast',
        headers={'Content-Type': 'application/json', 'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'},
        json={"to": user_ids, "messages": [{"type": "image", "originalContentUrl": qrcode_url, "previewImageUrl": qrcode_url}]}
    )
    return response.status_code, response.text
