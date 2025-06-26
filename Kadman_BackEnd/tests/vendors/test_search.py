import json
import sys
import os
import pytest
from unittest.mock import patch

# Ensure project root is in sys.path to import app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from app import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

def test_search_only_shop_name(client):
    with patch("vendors.es") as mock_es, patch("vendors.syllable_tokenize") as mock_tokenize:
        mock_tokenize.return_value = ["testshop"]

        def mock_search(index, body, size=200):
            multi_match = body["query"]["bool"]["should"][0]["multi_match"]
            assert "shop_name" in multi_match["fields"]
            assert "badges" in multi_match["fields"]
            assert multi_match["query"] == "TestShop"
            return {"hits": {"hits": [{ "_source": {"vendorID": 1, "shop_name": "Test Shop", "badges": []}}]}}

        mock_es.search.side_effect = mock_search

        response = client.get("/search?q=Test Shop")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert data[0]["shop_name"] == "Test Shop"

def test_search_only_badges(client):
    with patch("vendors.es") as mock_es, patch("vendors.syllable_tokenize") as mock_tokenize:
        mock_tokenize.return_value = ["eco", "verified"]

        def mock_search(index, body, size=200):
            terms_query = body["query"]["bool"]["should"][1]["terms"]
            assert "shop_name_syllables" in terms_query
            assert "eco" in terms_query["shop_name_syllables"]
            assert "verified" in terms_query["shop_name_syllables"]

            return {"hits": {"hits": [{ "_source": {"vendorID": 2, "shop_name": "Badge Shop", "badges": ["eco", "verified"]}}]}}

        mock_es.search.side_effect = mock_search

        response = client.get("/search?q=eco verified")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 1
        assert "eco" in data[0]["badges"]
        assert "verified" in data[0]["badges"]

def test_search_empty_query(client):
    with patch("vendors.es") as mock_es, patch("vendors.syllable_tokenize") as mock_tokenize:
        mock_tokenize.return_value = []

        def mock_search(index, body, size=200):
            assert "match_all" in body["query"]
            return {"hits": {"hits": [
                {"_source": {"vendorID": 1, "shop_name": "Shop1", "badges": []}},
                {"_source": {"vendorID": 2, "shop_name": "Shop2", "badges": ["verified"]}}
            ]}}

        mock_es.search.side_effect = mock_search

        response = client.get("/search?q=")
        assert response.status_code == 200

        data = json.loads(response.data)
        assert len(data) == 2
        assert data[0]["vendorID"] == 1
        assert data[1]["vendorID"] == 2
