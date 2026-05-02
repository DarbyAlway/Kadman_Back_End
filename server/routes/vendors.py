import json
import os
import re
import traceback
from flask import Blueprint, jsonify, request, Response
from dotenv import load_dotenv
from elasticsearch import Elasticsearch
from pythainlp.tokenize import syllable_tokenize
from db import get_db_connection
from routes.layouts import send_line_multicast, send_line_qrcode
from utils.vendor_tools import (
    get_vendor_by_lineid,
    update_vendor_attendance,
    calculate_attendance,
    update_layout,
    notify_vendor,
    update_vendor_attendance_days,
)

load_dotenv()

vendors_bp = Blueprint('vendors', __name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_Key')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:5173')

es = Elasticsearch(os.getenv('ELASTIC_URL', 'http://localhost:9200'))
INDEX_NAME = "kadman"


@vendors_bp.route("/update_badges", methods=["POST"])
def update_badges():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendor_id = data.get("vendorID")
        badges = data.get("badges")
        shop_name = data.get("shop_name")

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE vendors SET badges = %s WHERE vendorID = %s",
            (json.dumps(badges, ensure_ascii=False), vendor_id)
        )
        conn.commit()
        cursor.close()

        es.update(
            index=INDEX_NAME,
            id=vendor_id,
            body={"doc": {
                "shop_name": shop_name,
                "badges": badges,
                "shop_name_syllables": syllable_tokenize(shop_name)
            }}
        )
        return jsonify({"message": "Badges updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vendors_bp.route("/search", methods=["GET"])
def search():
    query_text = request.args.get("q", "")
    cleaned_query = re.sub(r'["\'\s]+', '', query_text)

    if cleaned_query:
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {"multi_match": {"query": cleaned_query, "fields": ["shop_name", "badges"]}},
                        {"terms": {"shop_name_syllables": syllable_tokenize(cleaned_query)}}
                    ]
                }
            }
        }
    else:
        query_body = {"query": {"match_all": {}}}

    try:
        result = es.search(index=INDEX_NAME, body=query_body, size=200)
        hits = result.get("hits", {}).get("hits", [])
        results = sorted([hit["_source"] for hit in hits], key=lambda x: x.get("vendorID"))
        return Response(json.dumps(results, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@vendors_bp.route("/get_all_vendors", methods=["GET"])
def get_all_vendors():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM vendors")
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return Response(json.dumps(results, ensure_ascii=False), content_type="application/json")
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vendors_bp.route("/delete_selected_badges", methods=["POST"])
def delete_selected_badges():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendor_id = data.get("vendorID")
        badges_to_remove = data.get("badges")

        if not vendor_id or not isinstance(badges_to_remove, list):
            return jsonify({"error": "vendorID and list of badges are required"}), 400

        cursor = conn.cursor()
        cursor.execute("SELECT badges FROM vendors WHERE vendorID = %s", (vendor_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Vendor not found"}), 404

        current_badges = json.loads(result[0]) if result[0] else []
        updated_badges = [b for b in current_badges if b not in badges_to_remove]

        cursor.execute(
            "UPDATE vendors SET badges = %s WHERE vendorID = %s",
            (json.dumps(updated_badges, ensure_ascii=False), vendor_id)
        )
        conn.commit()
        cursor.close()

        es.index(index=INDEX_NAME, id=vendor_id, body={"vendorID": vendor_id, "badges": updated_badges})
        return jsonify({"message": "Badges removed", "badges_left": updated_badges}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vendors_bp.route("/add_vendors", methods=["POST"])
def add_vendors():
    conn = get_db_connection()
    try:
        data = request.get_json()
        shop_name = data.get("shop_name")
        badges = data.get("badges")

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO vendors (shop_name, badges) VALUES (%s, %s)",
            (shop_name, json.dumps(badges, ensure_ascii=False) if badges else None)
        )
        vendor_id = cursor.lastrowid
        conn.commit()
        cursor.close()

        es.index(
            index=INDEX_NAME, id=vendor_id,
            body={"vendorID": vendor_id, "shop_name": shop_name, "badges": badges,
                  "shop_name_syllables": syllable_tokenize(shop_name)}
        )
        return jsonify({"message": "Vendor added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@vendors_bp.route("/increase_attendance", methods=["POST"])
def increase_num_of_attendance():
    conn = get_db_connection()
    try:
        vendor_id = request.get_json().get("vendorID")
        cursor = conn.cursor()
        cursor.execute("UPDATE vendors SET attendance = attendance + 1 WHERE vendorID = %s", (vendor_id,))
        conn.commit()
        return jsonify({"message": "Attendance increased successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@vendors_bp.route("/decrease_attendance", methods=["POST"])
def decrease_num_of_attendance():
    conn = get_db_connection()
    try:
        vendor_id = request.get_json().get("vendorID")
        cursor = conn.cursor()
        cursor.execute("UPDATE vendors SET attendance = attendance - 1 WHERE vendorID = %s", (vendor_id,))
        conn.commit()
        return jsonify({"message": "Attendance decreased successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@vendors_bp.route("/reset_attendance", methods=["POST"])
def reset_attendance():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE vendors SET attendance = 3")
        conn.commit()
        return jsonify({"message": "All vendor attendance reset to 3"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()


@vendors_bp.route("/check_attendance/<int:layout_id>", methods=['POST'])
def check_attendance(layout_id):
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        user_id = data.get('userId')
        days = data.get('days')
        if user_id is None or days is None:
            return jsonify({"error": "Missing required fields"}), 400

        days_count = len(days) if isinstance(days, list) else 0
        conn = get_db_connection()
        cursor = conn.cursor()

        vendor_row = get_vendor_by_lineid(cursor, user_id)
        if not vendor_row:
            return jsonify({"error": "Vendor not found"}), 404
        vendor_id, current_attendance = vendor_row

        new_attendance = calculate_attendance(current_attendance, days_count)
        update_vendor_attendance(cursor, vendor_id, new_attendance)
        days_json = update_vendor_attendance_days(cursor, vendor_id, days)

        cursor.execute(
            "UPDATE vendors SET payment = %s WHERE vendorID = %s",
            (len(days) * 100, vendor_id)
        )

        layout_data, updated = update_layout(cursor, layout_id, vendor_id)
        if not updated:
            return jsonify({"error": "Vendor not found in layout"}), 404

        conn.commit()

        status_code, _ = notify_vendor(user_id, f"{FRONTEND_URL}/payment")

        return jsonify({
            "message": "Attendance recorded and notification sent",
            "vendorID": vendor_id,
            "days_checked": days,
            "old_attendance": current_attendance,
            "new_attendance": new_attendance,
            "attendance_days": days_json,
            "layout_updated": updated,
            "line_status": status_code
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@vendors_bp.route("/get_quota", methods=['POST'])
def get_quota():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request body must be JSON"}), 400

        line_id = data.get("lineID") or data.get("userId")
        if not line_id:
            return jsonify({"error": "lineID or userId is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT attendance FROM vendors WHERE lineID = %s", (line_id,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": f"No vendor found with lineID {line_id}"}), 404

        return jsonify({"lineID": line_id, "attendance": row["attendance"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


@vendors_bp.route("/get_payment/<int:vendorID>", methods=["GET"])
def get_payment(vendorID):
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT payment FROM vendors WHERE vendorID = %s", (vendorID,))
        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": f"No vendor found with vendorID {vendorID}"}), 404

        return jsonify({"vendorID": vendorID, "payment": row["payment"]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
