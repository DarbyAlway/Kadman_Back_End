import pytest
import json
from unittest.mock import patch, MagicMock
from app import app
from pathlib import Path

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("layouts.get_db_connection")
def test_update_layout_using_mock_json(mock_get_db, client):
    # Load mock json
    json_path = Path(__file__).parent / "mocks" / "layouts_dump.json"
    with json_path.open(encoding="utf-8") as f:
        layouts = json.load(f)

    # Take the first layout to simulate update
    layout = layouts[0]
    layout_id = layout["id"]

    data_dict = json.loads(layout["data"]) # Convert stringified JSON to dict

    updated_layout = {
    "name": layout["name"] + "_updated",
    "data": data_dict
    }

    updated_layout["data"]["A1"]["shop_name"] = "ร้านใหม่"
   
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    
    response = client.put(
        f"/update_layout/{layout_id}",
        data=json.dumps(updated_layout),
        content_type="application/json"
    )

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {"message": "Layout updated successfully"}

    # Make sure the query was executed
    mock_cursor.execute.assert_called_once()
    args = mock_cursor.execute.call_args[0] # query from fake cursor

    expected_query = "UPDATE layouts SET name = %s, data = %s WHERE id = %s"
    assert args[0] == expected_query # Check query from real cursor and fake cursor
    assert args[1][0] == updated_layout["name"]
    assert json.loads(args[1][1]) == updated_layout["data"]  # stringified JSON was passed
    assert args[1][2] == layout_id

    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
