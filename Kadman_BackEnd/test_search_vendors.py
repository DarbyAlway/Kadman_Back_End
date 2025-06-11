import pytest
import json
from unittest.mock import MagicMock
from flask import Flask

from vendors import vendors_bp

@pytest.fixture
def client():
    app = Flask(__name__)
    app.register_blueprint(vendors_bp)
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_search_with_query(monkeypatch, client):
    # Mock Elasticsearch client and its search method
    mock_es = MagicMock()
    mock_response = {
        "hits": {
            "hits": [
                {"_source": {"vendorID": "v1", "shop_name": "Shop1", "badges": ["verified"]}},
                {"_source": {"vendorID": "v2", "shop_name": "Shop2", "badges": ["top-rated"]}},
            ]
        }
    }
    
    mock_es.search.return_value = mock_response

    # Patch the global 'es' variable inside vendors module to use the mock
    monkeypatch.setattr("vendors.es", mock_es)

    # Perform GET request with query parameter ?q=shop
    response = client.get("/search?q=shop")

    # Assert HTTP 200 OK
    assert response.status_code == 200

    # Parse JSON response
    data = response.get_json()

    # Check if results match expected mock data sorted by vendorID
    expected = sorted(
        [hit["_source"] for hit in mock_response["hits"]["hits"]],
        key=lambda x: x.get("vendorID")
    )
    assert data == expected

    # Verify that the mock es.search was called once
    mock_es.search.assert_called_once()

def test_search_empty_query(monkeypatch, client):
    # Mock Elasticsearch client and its search method
    mock_es = MagicMock()
    mock_response = {
        "hits": {
            "hits": [
                {"_source": {"vendorID": "v3", "shop_name": "Shop3", "badges": []}}
            ]
        }
    }
    mock_es.search.return_value = mock_response

    monkeypatch.setattr("vendors.es", mock_es)

    # Perform GET request without query parameter
    response = client.get("/search")

    assert response.status_code == 200

    data = response.get_json()

    expected = sorted(
        [hit["_source"] for hit in mock_response["hits"]["hits"]],
        key=lambda x: x.get("vendorID")
    )
    assert data == expected

    mock_es.search.assert_called_once()
