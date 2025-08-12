from flask import Flask, request, jsonify
import boto3
from botocore.exceptions import ClientError
from botocore import UNSIGNED
from botocore.client import Config

app = Flask(__name__)

# Configure your S3 bucket name here
S3_BUCKET = "kadmanbucket1"
S3_REGION = "ap-southeast-2"  # e.g. us-east-1

# Initialize boto3 S3 client
s3_client = boto3.client('s3', region_name=S3_REGION, config=Config(signature_version=UNSIGNED))

@app.route('/test-s3-connection', methods=['GET'])
def test_s3_connection():
    try:
        # Try to list objects to test the connection and permission
        response = s3_client.list_objects_v2(Bucket=S3_BUCKET, MaxKeys=1)
        return jsonify({"message": "Connected to S3 successfully!", "objects_found": response.get('KeyCount', 0)})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        s3_client.upload_fileobj(
            file,
            S3_BUCKET,
            file.filename,
            ExtraArgs={'ACL': 'bucket-owner-full-control'}
        )
        file_url = f"https://{S3_BUCKET}.s3.{S3_REGION}.amazonaws.com/{file.filename}"
        return jsonify({"message": "Upload successful", "file_url": file_url})
    except ClientError as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
