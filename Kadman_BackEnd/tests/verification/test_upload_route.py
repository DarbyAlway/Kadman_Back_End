import io
import json
import pytest
from unittest.mock import patch, MagicMock
from app import verification_bp  # adjust to your actual Flask app
from flask import Flask
from db import get_db_connection
from app import app
import requests
# ----------------------------
# Setup Flask test client
# ----------------------------
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(verification_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

# ----------------------------
# Test upload endpoint
# ----------------------------
@patch("verification.s3_client")
@patch("verification.requests.post")
@patch("verification.get_db_connection")

def test_upload_success(mock_db_conn, mock_requests_post, mock_s3_client, client):
    # --- Mock file ---
    file_content = b"dummy slip content"
    data = {
        "userId": "U12345",
        "displayName": "Test User",
        "paymentSlip": (io.BytesIO(file_content), "slip.jpg")
    }

    # --- Mock DB ---
    mock_cursor = MagicMock()
    # fetchone for duplicate check returns None
    mock_cursor.fetchone.side_effect = [None, {"vendorID": 1, "payment": "200"}]
    # fetchall for layouts
    mock_cursor.fetchall.return_value = [
        {"id": 1, "data": json.dumps({"A1": {"vendorID": 1, "status": "waiting"}})}
    ]
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    # --- Mock EasySlip response ---
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "data": {"transRef": "REF123", "amount": {"amount": 200}}
    }
    mock_requests_post.return_value = mock_response

    # --- Call endpoint ---
    response = client.post("/upload", data=data, content_type="multipart/form-data")

    # --- Assertions ---
    assert response.status_code == 200
    resp_json = response.get_json()
    assert resp_json["message"] == "Upload successful and verified"
    assert "file_url" in resp_json
    assert resp_json["user_id"] == "U12345"
    assert resp_json["display_name"] == "Test User"
    assert len(resp_json["updated_layouts"]) == 1
    assert resp_json["updated_layouts"][0]["updated_data"]["A1"]["status"] == "already paid"

    # --- Verify DB updates ---
    mock_cursor.execute.assert_any_call(
        "INSERT INTO SlipHistory (SlipHistory_ref) VALUES (%s)", ("REF123",)
    )
    mock_cursor.execute.assert_any_call(
        "UPDATE vendors SET payment = %s WHERE vendorID = %s", ("paid", 1)
    )
    mock_cursor.execute.assert_any_call(
        "UPDATE layouts SET data = %s WHERE id = %s",
        (json.dumps({"A1": {"vendorID": 1, "status": "already paid"}}), 1)
    )

    # --- Verify S3 upload called ---
    mock_s3_client.upload_fileobj.assert_called_once()
    # --- Verify EasySlip API called ---
    mock_requests_post.assert_called_once()
