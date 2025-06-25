import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("vendors.get_db_connection")  # adjust if your module name is different
def test_get_all_vendors(mock_get_db, client):
    # Mock DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Define fake result data
    fake_vendors = [
        {"vendorID": 1, "shop_name": "Vendor A", "badges": ["eco"]},
        {"vendorID": 2, "shop_name": "Vendor B", "badges": ["verified"]}
    ]
    mock_cursor.fetchall.return_value = fake_vendors

    # Send GET request
    response = client.get("/get_all_vendors")

    # Validate response
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert json.loads(response.data.decode("utf-8")) == fake_vendors

    # Ensure DB connection was used correctly
    mock_cursor.execute.assert_called_once_with("SELECT * FROM vendors")
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
