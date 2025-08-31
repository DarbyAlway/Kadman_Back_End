import pytest
from unittest.mock import patch, MagicMock
from flask import Flask, json
from vendors import vendors_bp  # adjust to your blueprint

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(vendors_bp)
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

@patch("vendors.notify_vendor")
@patch("vendors.update_layout")
@patch("vendors.update_vendor_attendance_days")
@patch("vendors.update_vendor_attendance")
@patch("vendors.get_vendor_by_lineid")
@patch("vendors.get_db_connection")
def test_check_attendance(mock_db_conn, mock_get_vendor, mock_update_attendance,
                          mock_update_days, mock_update_layout, mock_notify, client):
    # --- Mock database ---
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_db_conn.return_value = mock_conn

    # --- Mock vendor lookup ---
    vendor_id = 101
    current_attendance = 5
    mock_get_vendor.return_value = (vendor_id, current_attendance)

    # --- Mock update functions ---
    mock_update_attendance.return_value = None
    mock_update_days.return_value = '["Mon","Tue"]'
    mock_update_layout.return_value = ({"A1":{"vendorID":vendor_id,"status":"pending payment"}}, True)
    mock_notify.return_value = (200, "sent")

    # --- Request data ---
    layout_id = 1
    data = {
        "userId": "U12345",
        "displayName": "Test Vendor",
        "days": ["Mon","Tue"]
    }

    # --- Call endpoint ---
    response = client.post(f"/check_attendance/{layout_id}",
                           data=json.dumps(data),
                           content_type="application/json")

    # --- Assertions ---
    assert response.status_code == 200
    resp_json = response.get_json()
    assert resp_json["vendorID"] == vendor_id
    assert resp_json["days_checked"] == ["Mon","Tue"]
    assert resp_json["old_attendance"] == current_attendance
    assert resp_json["new_attendance"] == 4  # 5 - 1 (2 days)
    assert resp_json["attendance_days"] == '["Mon","Tue"]'
    assert resp_json["layout_updated"] is True
    assert resp_json["line_status"] == 200

    # --- Verify database calls ---
    mock_update_attendance.assert_called_once_with(mock_cursor, vendor_id, 4)
    mock_update_days.assert_called_once_with(mock_cursor, vendor_id, ["Mon","Tue"])
    mock_update_layout.assert_called_once_with(mock_cursor, layout_id, vendor_id)
    mock_cursor.execute.assert_any_call(
        "UPDATE vendors SET payment = %s WHERE vendorID = %s",
        (200, vendor_id)
    )
    mock_conn.commit.assert_called()
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()

    # --- Verify notification ---
    mock_notify.assert_called_once()
