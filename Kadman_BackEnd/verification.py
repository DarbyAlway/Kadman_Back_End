from flask import Flask, request, jsonify
import boto3
import requests
from botocore.client import Config
import os
import io
from botocore import UNSIGNED
from flask import Blueprint
from db import get_db_connection
import json
app = Flask(__name__)
verification_bp = Blueprint('verification',__name__)

# S3 config
S3_BUCKET = "kadmanbucket1"
S3_REGION = "ap-southeast-2" 
# EasySlip config
EASYSLIP_API = "https://developer.easyslip.com/api/v1/verify"
EASYSLIP_TOKEN = os.getenv('EASY_SLIP_KEY')
# Initialize boto3 S3 client
s3_client = boto3.client('s3', region_name=S3_REGION, config=Config(signature_version=UNSIGNED))

@verification_bp.route('/upload', methods=['POST'])
def upload():
    if 'paymentSlip' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['paymentSlip']
    if not file or file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    user_id = request.form.get("userId")       # LINE ID
    display_name = request.form.get("displayName")

    try:
        # === Step 1: Upload to S3 ===
        file_bytes = file.read()
        s3_buffer = io.BytesIO(file_bytes)
        s3_client.upload_fileobj(
            s3_buffer,
            S3_BUCKET,
            file.filename,
            ExtraArgs={'ACL': 'bucket-owner-full-control'}
        )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        print(f"✅ File uploaded to S3: {file_url}")

        # === Step 2: Send to EasySlip for verification ===
        slip_buffer = io.BytesIO(file_bytes)
        headers = {"Authorization": f"Bearer {EASYSLIP_TOKEN}"}
        files = {"file": (file.filename, slip_buffer, file.content_type)}
        response = requests.post(EASYSLIP_API, headers=headers, files=files)

        if response.status_code != 200:
            return jsonify({
                "message": "Upload successful but EasySlip verification failed",
                "file_url": file_url,
                "user_id": user_id,
                "display_name": display_name,
                "easyslip_error": response.text
            }), response.status_code

        easyslip_data = response.json()

        # === Step 3: Update DB: vendors and layouts ===
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 3a: Find vendor by LINE ID
        cursor.execute("SELECT vendorID FROM vendors WHERE lineID = %s", (user_id,))
        vendor = cursor.fetchone()
        if not vendor:
            cursor.close()
            conn.close()
            return jsonify({"error": "Vendor not found for this LINE ID"}), 404

        vendor_id = vendor["vendorID"]
        print(f"Vendor found: {vendor_id}")

        # 3b: Update vendor payment
        cursor.execute("UPDATE vendors SET payment = %s WHERE vendorID = %s", ("paid", vendor_id))
        conn.commit()
        print(f"Vendor {vendor_id} payment set to 'paid'")

        # 3c: Update all layouts where this vendor exists
        cursor.execute("SELECT id, data FROM layouts")
        layouts = cursor.fetchall()
        updated_layouts = []

        for layout in layouts:
            layout_id = layout["id"]
            data_json = layout["data"]

            if not data_json:
                continue

            try:
                data = json.loads(data_json)
            except json.JSONDecodeError:
                continue

            updated = False
            for block_key, block_value in data.items():
                if block_value.get("vendorID") == vendor_id:
                    print(f"Updating layout {layout_id} block {block_key} status to 'already paid'")
                    block_value["status"] = "already paid"
                    updated = True

            if updated:
                cursor.execute(
                    "UPDATE layouts SET data = %s WHERE id = %s",
                    (json.dumps(data), layout_id)
                )
                updated_layouts.append({"layout_id": layout_id, "updated_data": data})

        conn.commit()
        cursor.close()
        conn.close()

        # === Step 4: Return success ===
        return jsonify({
            "message": "Upload successful and verified",
            "file_url": file_url,
            "user_id": user_id,
            "display_name": display_name,
            "easyslip_response": easyslip_data,
            "updated_layouts": updated_layouts
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500