import pytest
import json
from unittest.mock import patch, MagicMock
from app import app
from pathlib import Path

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("layouts.send_line_multicast")
@patch("layouts.get_db_connection")
def test_send_notification_with_mock_json(mock_get_db, mock_send_line, client):
    # Load mock layout data from JSON file
    json_path = Path("mocks/layouts_dump.json")
    with json_path.open(encoding="utf-8") as f:
        layouts = json.load(f)

    # Pick a layout with known vendorIDs
    layout = layouts[0]
    layout_id = layout["id"]
    layout_data_dict = json.loads(layout["data"])  
    layout_data_str = json.dumps(layout_data_dict, ensure_ascii=False)

    # Mock database connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Build side_effect for .fetchone():
    side_effects = [(layout_data_str,)]  # First SELECT: get layout
#     layout_data_str = [(layout_data_str,),         #
#     ("line-id-1",),             
#     (None,),                    
# ]
    
    
    for slot in layout_data_dict.values():
        vendor_id = slot.get("vendorID")
        if vendor_id == 1:
            side_effects.append(("line-id-1",))  # mock Line ID for vendor 1
        else: 
            side_effects.append((None,))  

    mock_cursor.fetchone.side_effect = side_effects
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Mock LINE notification
    mock_send_line.return_value = (200, "OK")

    # Perform GET request
    response = client.get(f"/send_notification/{layout_id}")
    assert response.status_code == 200
    response_json = response.get_json()

    # Check response per slot
    for i, (slot_key, slot_value) in enumerate(layout_data_dict.items()):
        expected_vendor_id = slot_value["vendorID"]
        if expected_vendor_id == 1:
            assert response_json[i]["notification_status"] == 200
            assert response_json[i]["notification_response"] == "OK"
            assert response_json[i]["vendorID"] == 1
            assert response_json[i]["lineID"] == "line-id-1"
        else:
            assert response_json[i]["notification_status"] == "skipped"
            assert response_json[i]["notification_response"] == "No LINE user ID found"
            assert response_json[i]["lineID"] is None

    # Verify LINE call was made only once for vendor 1
    mock_send_line.assert_called_once_with(
        ["line-id-1"],
        f"Notification for layout ID {layout_id} - Slot A1 \n ⚠️⚠️(This is Send Batch Notification demo. Attendance feature will be implement in progress 2)⚠️⚠️"
    )

    mock_cursor.close.assert_called_once()
