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
def test_show_all_layouts_from_json_file(mock_get_db, client):
    # 1. Load JSON from file
    json_path = Path(__file__).parent / "mocks" / "layouts_dump.json"
    with json_path.open(encoding="utf-8") as f:
        json_data = json.load(f)

    # 2. Convert list of dicts to mock DB rows (tuples)
    mock_rows = []
    for row in json_data:
        mock_rows.append((
            row["id"],
            row["name"],
            json.dumps(row["data"], ensure_ascii=False)  # simulate DB JSON string
        ))

    # 3. Mock DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = mock_rows
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # 4. Call the API
    response = client.get("/show_all_layouts")

    # 5. Assertions
    assert response.status_code == 200
    returned = json.loads(response.data)
    assert returned == json_data  # compare actual vs expected

    # 6. Check DB call
    mock_cursor.execute.assert_called_once_with("SELECT * FROM layouts")
    mock_cursor.close.assert_called_once()
