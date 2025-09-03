import json
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from layouts import layouts_bp   # adjust import path to your app

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(layouts_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_begin_attendance_success(client):
    # --- Mock database connection ---
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Mock layout data from DB
    layout_data = json.dumps({
        "A1": {"vendorID": 123}
    })
    mock_cursor.fetchone.side_effect = [
        (layout_data,),           # first fetchone() for layouts
        ("line_user_abc",),       # second fetchone() for vendors
    ]

    # --- Mock helper functions ---
    with patch("layouts.get_db_connection", return_value=mock_conn), \
         patch("layouts.send_line_multicast", return_value=(200, "OK")), \
         patch("layouts.change_all_status_to_pending_attendance") as mock_change, \
         patch("layouts.activate_layout_status") as mock_activate:

        response = client.get("/begin_attendance/1")
        data = response.get_json()

        # --- Assertions ---
        assert response.status_code == 200
        assert isinstance(data, list)
        assert data[0]["slot"] == "A1"
        assert data[0]["vendorID"] == 123
        assert data[0]["lineID"] == "line_user_abc"
        assert data[0]["notification_status"] == 200
        assert data[0]["notification_response"] == "OK"

        mock_change.assert_called_once_with(1, mock_conn, mock_cursor)
        mock_activate.assert_called_once_with(1, mock_conn, mock_cursor)
        mock_conn.commit.assert_called_once()


def test_begin_attendance_layout_not_found(client):
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    # Simulate no row found
    mock_cursor.fetchone.return_value = None

    with patch("layouts.get_db_connection", return_value=mock_conn):
        response = client.get("/begin_attendance/999")
        data = response.get_json()

        assert response.status_code == 404
        assert "Layout with ID 999 not found" in data["error"]
