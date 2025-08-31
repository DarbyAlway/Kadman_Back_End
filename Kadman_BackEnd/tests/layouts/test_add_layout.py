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
def test_insert_layout_with_old_and_new_mock_data(mock_get_db, client):
    # Load old layouts (existing data)
    json_path = Path(__file__).parent / "mocks" / "layouts_dump.json"
    with json_path.open(encoding="utf-8") as f:
        old_layouts = json.load(f)

    # Your new layout to insert
    new_layout = {
        "name": "new_layout",
        "data": {
            "C1": {"vendorID": 10, "shop_name": "ร้านใหม่"}
        }
    }

    # Setup mock DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.lastrowid = 999  # mock new inserted ID

    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn


    # Send POST request to insert new layout
    response = client.post(
        "/insert_layout",
        data=json.dumps(new_layout),
        content_type="application/json"
    )

    # Assertions on response
    assert response.status_code == 201
    resp_json = response.get_json()
    assert resp_json["message"] == "Layout added successfully"
    assert resp_json["id"] == 999

    # Verify SQL INSERT was called with correct data
    mock_cursor.execute.assert_called_once()
    query, values = mock_cursor.execute.call_args[0]

    expected_query = "INSERT INTO layouts (name, data) VALUES (%s, %s)"
    assert query == expected_query
    assert values[0] == new_layout["name"]

    # Normalize JSON comparison
    inserted_data = json.loads(values[1])
    assert inserted_data == new_layout["data"]

