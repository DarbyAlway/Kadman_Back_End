import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("vendors.es")
@patch("vendors.get_db_connection")
def test_delete_selected_badges(mock_get_db, mock_es, client):
    from vendors import INDEX_NAME  # 🧠 import inside the test (optional for clarity)

    request_data = {
        "vendorID": 1,
        "badges": ["เสื้อผ้า", "ร้านค้าแนะนำ"]
    }

    current_badges = json.dumps(["ร้านค้าแนะนำ", "จัดส่งฟรี", "แว่นตา"], ensure_ascii=False)
    updated_badges = ["จัดส่งฟรี", "แว่นตา"] 

    # Set up DB mock
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn
    mock_cursor.fetchone.return_value = (current_badges,)

    # Use context manager to patch INDEX_NAME during the test
    with patch("vendors.INDEX_NAME", "kadman"):
        response = client.post(
            "/delete_selected_badges",
            data=json.dumps(request_data, ensure_ascii=False),
            content_type="application/json"
        )

    # Assertions
    assert response.status_code == 200
    assert response.json == {
        "message": "Selected badges removed",
        "badges left": updated_badges
    }

    expected_updated_json = json.dumps(updated_badges, ensure_ascii=False)
    mock_cursor.execute.assert_any_call(
        "UPDATE vendors SET badges = %s WHERE vendorID = %s",
        (expected_updated_json, 1)
    )

    mock_es.index.assert_called_once_with(
        index="kadman",
        id=1,
        body={
            "vendorID": 1,
            "badges": updated_badges
        }
    )
