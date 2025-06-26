import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("vendors.INDEX_NAME", "kadman")
@patch("vendors.es")
@patch("vendors.get_db_connection")
@patch("vendors.syllable_tokenize")
def test_add_vendors(mock_tokenize, mock_get_db, mock_es, client):
    # Input data with Thai values
    request_data = {
        "shop_name": "ร้านน่ารัก",
        "badges": ["เสื้อผ้า", "จัดส่งฟรี"]
    }

    # Expected Elasticsearch tokenization result
    mock_tokenize.return_value = ["ร้าน", "น่า", "รัก"]

    # Setup DB mock
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_cursor.lastrowid = 10  # Simulate new vendor ID
    mock_get_db.return_value = mock_conn

    # Call the endpoint
    response = client.post(
        "/add_vendors",
        data=json.dumps(request_data, ensure_ascii=False),
        content_type="application/json"
    )

    # ✅ Check response
    assert response.status_code == 201
    assert response.json["message"] == "Vendor added successfully"

    # ✅ Check DB insert
    expected_json_badges = json.dumps(request_data["badges"], ensure_ascii=False)
    mock_cursor.execute.assert_called_once_with(
        "INSERT INTO vendors (shop_name, badges) VALUES (%s, %s)",
        ("ร้านน่ารัก", expected_json_badges)
    )
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

    #  Check Elasticsearch indexing
    mock_es.index.assert_called_once_with(
        index="kadman",  # or patch INDEX_NAME
        id=10,
        body={
            "vendorID": 10,
            "shop_name": "ร้านน่ารัก",
            "badges": ["เสื้อผ้า", "จัดส่งฟรี"],
            "shop_name_syllables": ["ร้าน", "น่า", "รัก"]
        }
    )
