import os
from flask import Blueprint, request, jsonify
import boto3
import requests
from botocore.exceptions import ClientError
from werkzeug.utils import secure_filename

payment_bp = Blueprint('payment_bp', __name__)

# AWS S3 config
AWS_S3_BUCKET = "your-bucket-name"
AWS_S3_REGION = "your-region"  # e.g., us-east-1

s3_client = boto3.client('s3', region_name=AWS_S3_REGION)

EASYSLIP_API_URL = "https://api.easyslip.com/parse"
EASYLIP_API_KEY = "YOUR_API_KEY_HERE"

EXPECTED_AMOUNT = 500
EXPECTED_RECEIVER = "Your Shop Name"


def upload_file_to_s3(file_obj, filename):
    try:
        s3_client.upload_fileobj(file_obj, AWS_S3_BUCKET, filename, ExtraArgs={'ACL': 'public-read'})
        file_url = f"https://{AWS_S3_BUCKET}.s3.{AWS_S3_REGION}.amazonaws.com/{filename}"
        return file_url
    except ClientError as e:
        print(f"S3 upload error: {e}")
        return None


@payment_bp.route('/upload-slip', methods=['POST'])
def upload_slip():
    if 'paymentSlip' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['paymentSlip']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)

    # Upload to S3
    file_url = upload_file_to_s3(file, filename)
    if not file_url:
        return jsonify({"error": "Failed to upload file to S3"}), 500

    # Download file back to send to EasySlip API
    try:
        file_content = requests.get(file_url).content

        response = requests.post(
            EASYSLIP_API_URL,
            headers={'Authorization': f'Bearer {EASYLIP_API_KEY}'},
            files={'file': (filename, file_content)}
        )

        if response.status_code != 200:
            return jsonify({"error": "Failed to parse slip"}), 500

        slip_data = response.json()

        amount = slip_data.get('amount')
        receiver_name = slip_data.get('receiver', {}).get('accountName')

        if amount == EXPECTED_AMOUNT and receiver_name == EXPECTED_RECEIVER:
            return jsonify({"success": True, "message": "Payment verified", "fileUrl": file_url})
        else:
            return jsonify({
                "success": False,
                "message": f"Mismatch: amount={amount}, receiver={receiver_name}",
                "fileUrl": file_url
            })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
