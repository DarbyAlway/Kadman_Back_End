from flask import Blueprint, jsonify, request
from db import get_db_connection
import json 
from pythainlp.tokenize import syllable_tokenize
from elasticsearch import Elasticsearch
import re
import os
from dotenv import load_dotenv
from flask import Response
import traceback
import requests
from layouts import send_line_multicast,send_line_qrcode
import io
import qrcode
from flask import send_file
import urllib.parse
from promptpay import qrcode
from vendor_tools import (
    get_vendor_by_lineid,
    update_vendor_attendance,
    calculate_attendance,
    update_layout,
    notify_vendor,
    update_vendor_attendance_days,
)

vendors_bp = Blueprint('vendors', __name__)# Vendors Blueprint
load_dotenv()  # Load environment variables from .env file
ES_KEY = os.getenv('ES_KEY')
PROMPTPAY_NUMBER = "0864395473"
CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_Key')


es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', ES_KEY)),
    ca_certs=os.path.expanduser("~/http_ca.crt") 
)

INDEX_NAME = "kadman"  

# Update vendors badges
@vendors_bp.route("/update_badges",methods=["POST"])
def update_badges():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        data = request.get_json()
        vendorID = data.get("vendorID")
        badge_name = data.get("badges")  # this is already a Python list
        shop_name = data.get("shop_name")

        # Save to MySQL
        sql = "UPDATE vendors SET badges = %s WHERE vendorID = %s"
        badge_json = json.dumps(badge_name, ensure_ascii=False)
        cursor.execute(sql, (badge_json, vendorID))
        print(f"Rows affected: {cursor.rowcount}")
        conn.commit()
        cursor.close()
        print(type(badge_name))
        es.update(
            index=INDEX_NAME,
            id=vendorID,
            body={
                "doc": {
                    "shop_name":shop_name,
                    "badges": badge_name,  # not badge_json
                    "shop_name_syllables": syllable_tokenize(shop_name)
                }
            }
        )
        print(badge_name)
        return jsonify({"message": "Badges added successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500




@vendors_bp.route("/search", methods=["GET"])
def search():
    query_text = request.args.get("q", "")
    cleaned_query = re.sub(r'["\'\s]+', '', query_text)

    if cleaned_query and cleaned_query != "":
        query_syllables = syllable_tokenize(cleaned_query)
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": cleaned_query,
                                "fields": ["shop_name", "badges"]
                            }
                        },
                        {
                            "terms": {
                                "shop_name_syllables": query_syllables
                            }
                        }
                    ]
                }
            }
        }
    else:
        query_body = {
            "query": {
                "match_all": {}
            }
        }
     
    try:
        result = es.search(index=INDEX_NAME, body=query_body, size=200)
        hits = result.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]
        results = sorted(results, key=lambda x: x.get("vendorID"))
        return Response(
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )

    except Exception as e:
        print("Exception in /search route:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


# return all vendors info from the database
@vendors_bp.route("/get_all_vendors", methods=["GET"])
def get_all_vendors():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vendors") #Query to get all vendors
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return Response(
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete selected badges from a vendors table
@vendors_bp.route("/delete_selected_badges", methods=["POST"])
def delete_selected_badges():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendorID = data.get("vendorID")
        badges_to_remove = data.get("badges")  # list of badges to remove

        if not vendorID or not isinstance(badges_to_remove, list):
            return jsonify({"error": "vendorID and list of badges are required"}), 400

        cursor = conn.cursor()

        # Get current badges
        cursor.execute("SELECT badges FROM vendors WHERE vendorID = %s", (vendorID,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Vendor not found"}), 404

        current_badges = json.loads(result[0]) if result[0] else []

        # Filter out the badges to remove
        updated_badges = [b for b in current_badges if b not in badges_to_remove]
        updated_json = json.dumps(updated_badges, ensure_ascii=False)

        # Update the DB
        cursor.execute("UPDATE vendors SET badges = %s WHERE vendorID = %s", (updated_json, vendorID))
        conn.commit()
        cursor.close()
 # Re-index this vendor in Elasticsearch with updated badges

        es.index(
            index=INDEX_NAME,
            id=vendorID,  # Use vendorID as the document ID
            body={
                "vendorID": vendorID,
                "badges": updated_badges,
            }
        )

        return jsonify({"message": "Selected badges removed", "badges left": updated_badges}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Add a new vendors to the database
@vendors_bp.route("/add_vendors", methods=["POST"])
def add_vendors():
    conn = get_db_connection()
    try:
        data = request.get_json()
        shop_name = data.get("shop_name")
        badges = data.get("badges")

        badge_json = json.dumps(badges, ensure_ascii=False) if badges else None
        cursor = conn.cursor()
        sql = "INSERT INTO vendors (shop_name, badges) VALUES (%s, %s)"
        cursor.execute(sql, (shop_name, badge_json))
        vendor_id = cursor.lastrowid  # Get the last inserted vendor ID
        print("New vendor ID:", vendor_id)
        conn.commit()
        cursor.close()

        # Indexing new vendor in Elasticsearch
        es.index(
            index=INDEX_NAME,
            id = vendor_id,
            body={
                "vendorID": vendor_id,
                "shop_name": shop_name,
                "badges": badges,
                "shop_name_syllables": syllable_tokenize(shop_name)
            }
        )

        return jsonify({"message": "Vendor added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# increase attendance  with specific vendorID    
@vendors_bp.route("/increase_attendance",methods=["POST"])
def increase_num_of_attendance():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendorID = data.get("vendorID")
        cur = conn.cursor()
        cur.execute("UPDATE vendors SET attendance = attendance + 1 WHERE vendorID = %s", (vendorID,))
        conn.commit()
        
        return {"message":"Attendance increased successfully"},200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        conn.close()
        
# decrease attendance with specific vendorID
@vendors_bp.route("/decrease_attendance",methods=["POST"])
def decrease_num_of_attendance():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendorID = data.get("vendorID")
        cur = conn.cursor()
        cur.execute("UPDATE vendors SET attendance = attendance - 1 WHERE vendorID = %s", (vendorID,))
        conn.commit()
        
        return {"message":"Attendance decreased successfully"},200
    except Exception as e:
        return {"error": str(e)}, 500
    finally:
        conn.close()

# reset all of attendance
@vendors_bp.route("/reset_attendance",methods=["POST"])
def reset_attendance():
    conn = get_db_connection()
    try:
        cur = conn.cursor()
        cur.execute("UPDATE vendors SET attendance = 3")
        conn.commit()
        return {"message":"all of vendor's attendance reset to 3 successfully"},200
    
    except Exception as e:
        return {"error":str(e)},500
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
        display_name = data.get('displayName')
        days = data.get('days')  # list of strings
        if user_id is None or days is None:
            return jsonify({"error": "Missing required fields"}), 400

        days_count = len(days) if isinstance(days, list) else 0

        conn = get_db_connection()
        cursor = conn.cursor()

        # --- Step 1: Find vendor ---
        vendor_row = get_vendor_by_lineid(cursor, user_id)
        if not vendor_row:
            return jsonify({"error": "Vendor not found"}), 404
        vendor_id, current_attendance = vendor_row
        print(f"✅ Vendor {vendor_id} found successfully (attendance={current_attendance})")

        # --- Step 2: Adjust attendance ---
        new_attendance = calculate_attendance(current_attendance, days_count)
        update_vendor_attendance(cursor, vendor_id, new_attendance)
        print(f"✅ Attendance updated successfully (old={current_attendance}, new={new_attendance})")

        # --- Step 2b: Save attendance days ---
        days_json = update_vendor_attendance_days(cursor, vendor_id, days)
        print(f"✅ Attendance days updated successfully: {days_json}")

        # --Step 2c: Calculate payment
        payment_amount = len(days) * 100
        cursor.execute(
            "UPDATE vendors SET payment = %s WHERE vendorID = %s",
            (payment_amount, vendor_id)
        )
        print(f"✅ Payment updated successfully: {payment_amount}")

        # --- Step 3: Update layout ---
        layout_data, updated = update_layout(cursor, layout_id, vendor_id)
        if not updated:
            return jsonify({"error": "Vendor not found in layout"}), 404
        print(f"✅ Layout {layout_id} updated successfully for vendor {vendor_id}")

        conn.commit()
        print("✅ Database changes committed successfully")

        # --- Step 4: Send notification for payment---
        payment_url = f'https://23922c7abf55.ngrok-free.app/payment' # Front end port
        status_code, response_text = notify_vendor(user_id, payment_url)
        print(f"✅ LINE notification sent successfully (status={status_code})")

        return jsonify({
            "message": "Attendance recorded and message sent",
            "vendorID": vendor_id,
            "days_checked": days,
            "old_attendance": current_attendance,
            "new_attendance": new_attendance,
            "attendance_days": days_json,
            "layout_updated": updated,
            "line_status": status_code
        }), 200

    except Exception as e:
        print("❌ Error in /vendors/check_attendance:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# get quota with specific line_id (from JSON body)
@vendors_bp.route("/get_quota", methods=['POST'])
def get_quota():
    conn = None
    cursor = None
    try:
        data = request.get_json()
        print("Received JSON from get_quota:", data)  # log incoming data

        if not data:
            print("❌ No JSON received in request body")
            return jsonify({"error": "Request body must be JSON"}), 400

        # accept either "lineID" or "userId" from frontend
        line_id = data.get("lineID") or data.get("userId")
        if not line_id:
            print("❌ Missing 'lineID' or 'userId' in JSON")
            return jsonify({"error": "lineID or userId is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Query to fetch quota for vendor with given lineID
        cursor.execute("SELECT attendance FROM vendors WHERE lineID = %s", (line_id,))
        row = cursor.fetchone()

        if row is None:
            print(f"❌ No vendor found with lineID {line_id}")
            return jsonify({"error": f"No vendor found with lineID {line_id}"}), 404

        print(f"✅ Vendor {line_id} has {row['attendance']} attendance left")
        return jsonify({
            "lineID": line_id,
            "attendance": row["attendance"]
        }), 200

    except Exception as e:
        print("❌ Exception in /get_quota:", str(e))
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# get payment with specific vendorID (via URL parameter)
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

        return jsonify({
            "vendorID": vendorID,
            "payment": row["payment"]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

