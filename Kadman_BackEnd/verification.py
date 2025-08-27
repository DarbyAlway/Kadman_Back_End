from flask import Flask, request, jsonify
import boto3
import requests
from botocore.client import Config
import os
import io
from botocore import UNSIGNED
from flask import Blueprint

app = Flask(__name__)
verification_bp = Blueprint('verification',__name__)

# S3 config
S3_BUCKET = "kadmanbucket1"
S3_REGION = "ap-southeast-2"() 
# EasySlip config
EASYSLIP_API = "https://developer.easyslip.com/api/v1/verify"
EASYSLIP_TOKEN = os.getenv('EASY_SLIP_KEY')

# Initialize boto3 S3 client
s3_client = boto3.client('s3', region_name=S3_REGION, config=Config(signature_version=UNSIGNED))

@verification_bp.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        # --- Step 1: Read file into memory once ---
        file_bytes = file.read()

        # --- Step 2: Upload to S3 ---
        s3_buffer = io.BytesIO(file_bytes)
        s3_buffer.seek(0)
        s3_client.upload_fileobj(
            s3_buffer,
            S3_BUCKET,
            file.filename,
            ExtraArgs={'ACL': 'bucket-owner-full-control'}
        )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        print(f"✅ File uploaded to S3: {file_url}")

        # --- Step 3: New buffer for EasySlip (so requests.post can close it safely) ---
        slip_buffer = io.BytesIO(file_bytes)
        headers = {"Authorization": f"Bearer {EASYSLIP_TOKEN}"}
        files = {"file": (file.filename, slip_buffer, file.content_type)}

        response = requests.post(EASYSLIP_API, headers=headers, files=files)

        print("📨 EasySlip Response Status:", response.status_code)
        print("📨 EasySlip Response Body:", response.text)

        if response.status_code == 200:
            return jsonify({
                "message": "Upload successful and verified",
                "file_url": file_url,
                "easyslip_response": response.json()
            })
        else:
            return jsonify({
                "message": "Upload successful but EasySlip verification failed",
                "file_url": file_url,
                "easyslip_error": response.text
            }), response.status_code

    except Exception as e:
        print("❌ Error:", str(e))
        return jsonify({"error": str(e)}), 500


