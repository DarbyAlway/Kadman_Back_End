import pytest
import json
from unittest.mock import patch, MagicMock

from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("layouts.get_db_connection")  # patch where the function is used, not where it's defined
def test_show_all_layouts(mock_get_db, client):
    # Mock the DB connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Sample database return data (as tuples)
    mock_cursor.fetchall.return_value = [
        (1, "Layout A", json.dumps({"x": 1, "y": 2})),
        (2, "Layout B", json.dumps({"x": 3, "y": 4}))
    ]
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Make the request
    response = client.get("/show_all_layouts")

    # Expected response data
    expected_data = [
        {"id": 1, "name": "Layout A", "data": {"x": 1, "y": 2}},
        {"id": 2, "name": "Layout B", "data": {"x": 3, "y": 4}}
    ]

    # Assertions
    assert response.status_code == 200
    assert response.content_type == "application/json"
    assert json.loads(response.data) == expected_data

    # Verify DB interaction
    mock_cursor.execute.assert_called_once_with("SELECT * FROM layouts")
    mock_cursor.close.assert_called_once()
