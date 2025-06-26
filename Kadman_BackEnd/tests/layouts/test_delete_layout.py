import pytest
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("layouts.get_db_connection")
def test_delete_layout_success(mock_get_db, client):
    layout_id = 123

    # Setup mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Simulate layout exists by returning a row on SELECT
    mock_cursor.fetchone.return_value = (layout_id,)
    
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Call DELETE API
    response = client.delete(f"/delete_layout/{layout_id}")

    # Assertions
    assert response.status_code == 200
    assert response.get_json() == {"message": f"Layout with ID {layout_id} deleted successfully"}

    # Check SQL SELECT and DELETE executed correctly
    # Select the layout id first then delete it
    calls = mock_cursor.execute.call_args_list
    assert calls[0][0][0] == "SELECT id FROM layouts WHERE id = %s" 
    assert calls[0][0][1] == (layout_id,)
    assert calls[1][0][0] == "DELETE FROM layouts WHERE id = %s"
    assert calls[1][0][1] == (layout_id,)

    # Check commit and close cursor
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

@patch("layouts.get_db_connection")
def test_delete_layout_not_found(mock_get_db, client):
    layout_id = 999

    # Setup mocks
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Simulate layout NOT found by returning None on SELECT
    mock_cursor.fetchone.return_value = None
    
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Call DELETE API
    response = client.delete(f"/delete_layout/{layout_id}")

    # Assertions
    assert response.status_code == 404
    assert response.get_json() == {"error": f"Layout with ID {layout_id} not found"}

    # Check SQL SELECT executed but DELETE not called
    mock_cursor.execute.assert_called_once_with("SELECT id FROM layouts WHERE id = %s", (layout_id,))
    mock_cursor.close.assert_called_once()
    mock_conn.commit.assert_not_called()
