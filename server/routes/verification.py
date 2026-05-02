import json
import io
import os
import requests
import boto3
from flask import Blueprint, jsonify, request
from botocore.client import Config
from botocore import UNSIGNED
from db import get_db_connection

verification_bp = Blueprint('verification', __name__)

S3_BUCKET = "kadmanbucket1"
S3_REGION = "ap-southeast-2"
EASYSLIP_API = "https://developer.easyslip.com/api/v1/verify"
EASYSLIP_TOKEN = os.getenv('EASY_SLIP_KEY')

s3_client = boto3.client('s3', region_name=S3_REGION, config=Config(signature_version=UNSIGNED))


@verification_bp.route('/upload', methods=['POST'])
def upload():
    if 'paymentSlip' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['paymentSlip']
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    user_id = request.form.get("userId")
    display_name = request.form.get("displayName")

    try:
        file_bytes = file.read()

        s3_client.upload_fileobj(
            io.BytesIO(file_bytes), S3_BUCKET, file.filename,
            ExtraArgs={'ACL': 'bucket-owner-full-control'}
        )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"

        response = requests.post(
            EASYSLIP_API,
            headers={"Authorization": f"Bearer {EASYSLIP_TOKEN}"},
            files={"file": (file.filename, io.BytesIO(file_bytes), file.content_type)}
        )

        if response.status_code != 200:
            return jsonify({
                "message": "Upload successful but verification failed",
                "file_url": file_url, "easyslip_error": response.text
            }), response.status_code

        easyslip_data = response.json()
        trans_ref = easyslip_data.get("data", {}).get("transRef")
        if not trans_ref:
            return jsonify({"error": "No transaction reference in EasySlip response"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT SlipHistory_id FROM SlipHistory WHERE SlipHistory_ref = %s", (trans_ref,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({"message": "Duplicate slip — already processed", "transRef": trans_ref}), 400

        cursor.execute("INSERT INTO SlipHistory (SlipHistory_ref) VALUES (%s)", (trans_ref,))
        conn.commit()

        cursor.execute("SELECT vendorID, payment FROM vendors WHERE lineID = %s", (user_id,))
        vendor = cursor.fetchone()
        if not vendor:
            cursor.close()
            conn.close()
            return jsonify({"error": "Vendor not found for this LINE ID"}), 404

        vendor_id = vendor["vendorID"]
        expected_payment = float(vendor["payment"])
        paid_amount = easyslip_data.get("data", {}).get("amount", {}).get("amount")

        if paid_amount is None:
            cursor.close()
            conn.close()
            return jsonify({"error": "Unable to read payment amount from EasySlip"}), 400

        if float(paid_amount) != expected_payment:
            cursor.close()
            conn.close()
            return jsonify({
                "message": "Payment amount mismatch",
                "expected": expected_payment, "paid": paid_amount
            }), 400

        cursor.execute("UPDATE vendors SET payment = %s WHERE vendorID = %s", ("paid", vendor_id))
        conn.commit()

        cursor.execute("SELECT id, data FROM layouts")
        updated_layouts = []
        for layout in cursor.fetchall():
            layout_id, data_json = layout["id"], layout["data"]
            if not data_json:
                continue
            try:
                data = json.loads(data_json)
            except json.JSONDecodeError:
                continue

            updated = False
            for block in data.values():
                if isinstance(block, dict) and block.get("vendorID") == vendor_id:
                    block["status"] = "already paid"
                    updated = True

            if updated:
                cursor.execute("UPDATE layouts SET data = %s WHERE id = %s", (json.dumps(data), layout_id))
                updated_layouts.append({"layout_id": layout_id, "updated_data": data})

        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            "message": "Payment verified successfully",
            "file_url": file_url, "user_id": user_id, "display_name": display_name,
            "easyslip_response": easyslip_data, "updated_layouts": updated_layouts
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
