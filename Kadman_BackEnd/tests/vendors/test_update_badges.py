import pytest
import json
from unittest.mock import patch, MagicMock
from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

@patch("vendors.get_db_connection")
@patch("vendors.es")
@patch("vendors.syllable_tokenize")
def test_update_badges(mock_tokenize, mock_es, mock_get_db, client):
    # Setup mock DB
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db.return_value = mock_conn

    # Setup mock tokenizer
    mock_tokenize.return_value = ["Test", "Shop"]

    # Mock request data
    request_data = {
        "vendorID": 1,
        "badges": ["eco", "verified"],
        "shop_name": "Test Shop"
    }

    response = client.post(
        "/update_badges",
        data=json.dumps(request_data),
        content_type="application/json"
    )

    assert response.status_code == 201
    assert response.json == {"message": "Badges added successfully"}

    # DB check
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()

    # ES check
    mock_es.update.assert_called_once()
    mock_tokenize.assert_called_once_with("Test Shop")


    # Indexing Test
    args,kwargs = mock_es.update.call_args
    # args = position arguments  (like ["abc", 1, {...}])
    # kwargs = keyword arguments (like {"index": "abc", "id": 1, "body": {...}})

    assert 'id' in kwargs # The call must have id  in kwargs 
    assert 'body' in kwargs  # The call must have body  in kwargs
    # Or if kwargs:
    assert kwargs.get('index') == "kadman" 
    assert kwargs.get('id') == request_data["vendorID"]
    body = kwargs.get('body')
    assert body is not None
    assert "doc" in body
    assert body["doc"]["badges"] == request_data["badges"]
    assert body["doc"]["shop_name"] == request_data["shop_name"]
