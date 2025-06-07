import pytest
import json
from flask import Flask
from unittest.mock import MagicMock
import sys
import os

from vendors import vendors_bp

# Set up a test app
@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(vendors_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_update_badges_success(monkeypatch, client):
    # Mock MySQL connection and Elasticsearch
    mock_cursor = MagicMock()
    mock_conn = MagicMock()
    mock_conn.cursor.return_value = mock_cursor

    mock_es = MagicMock()

    # Patch global `conn` and `es` used in the route
    monkeypatch.setattr("vendors.conn", mock_conn)
    monkeypatch.setattr("vendors.es", mock_es)

    # Example payload
    payload = {
        "vendorID": "v123",
        "badges": ["verified", "top-rated"],
        "shop_name": "Test Shop"
    }

    response = client.post(
        "/update_badges",
        data=json.dumps(payload),
        content_type='application/json'
    )

    assert response.status_code == 201
    assert response.get_json()["message"] == "Badges added successfully"

    # Assert SQL was executed
    mock_cursor.execute.assert_called_once()
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()

    # Assert Elasticsearch update called
    mock_es.update.assert_called_once()
