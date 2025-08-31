import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from vendors import vendors_bp  # adjust import to your blueprint

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(vendors_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

# ----------------------------
# Test reset_attendance
# ----------------------------
@patch("vendors.get_db_connection")
def test_reset_attendance(mock_db_conn, client):
    # Mock connection and cursor
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    # Call the endpoint
    response = client.post("/reset_attendance")

    # Check response
    assert response.status_code == 200
    resp_json = response.get_json()
    assert resp_json["message"] == "all of vendor's attendance reset to 3 successfully"

    # Check database call
    mock_cursor.execute.assert_called_once_with(
        "UPDATE vendors SET attendance = 3"
    )
    mock_conn.commit.assert_called()  # ensure commit was called
    mock_conn.close.assert_called()   # ensure connection was closed
