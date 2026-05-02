"""
Run this once to index vendor data into Elasticsearch.
Usage (from server/ directory): python scripts/indexing.py
"""
import json
import os
from pathlib import Path
from elasticsearch import Elasticsearch, helpers
from pythainlp.tokenize import syllable_tokenize
from dotenv import load_dotenv

SERVER_DIR = Path(__file__).parent.parent
load_dotenv(SERVER_DIR / ".env")

with open(SERVER_DIR / "data" / "vendors.json", encoding="utf-8") as f:
    vendors = json.load(f)

es = Elasticsearch(os.getenv("ELASTIC_URL", "http://localhost:9200"))
INDEX_NAME = "kadman"

if es.indices.exists(index=INDEX_NAME):
    es.indices.delete(index=INDEX_NAME)
    print("Old index deleted.")

es.indices.create(index=INDEX_NAME, body={
    "settings": {
        "analysis": {
            "tokenizer": {
                "edge_ngram_thai": {
                    "type": "edge_ngram", "min_gram": 2, "max_gram": 20,
                    "token_chars": ["letter", "digit"]
                }
            },
            "analyzer": {
                "thai_autocomplete": {
                    "type": "custom", "tokenizer": "edge_ngram_thai", "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "vendorID": {"type": "keyword"},
            "shop_name": {"type": "text", "analyzer": "thai_autocomplete", "search_analyzer": "thai_autocomplete"},
            "shop_name_syllables": {"type": "keyword"},
            "badges": {"type": "keyword"}
        }
    }
})
print(f"Index '{INDEX_NAME}' created.")

actions = [
    {
        "_index": INDEX_NAME,
        "_id": v["vendorID"],
        "_source": {
            "vendorID": v["vendorID"],
            "shop_name": v["shop_name"],
            "shop_name_syllables": syllable_tokenize(v["shop_name"]),
            "badges": v["badges"]
        }
    }
    for v in vendors
]

helpers.bulk(es, actions)
es.indices.refresh(index=INDEX_NAME)
print(f"Indexed {len(vendors)} vendors into '{INDEX_NAME}'.")

res = es.search(index=INDEX_NAME, query={"match_all": {}}, size=5)
print("\nSample results:")
for hit in res["hits"]["hits"]:
    print(" ", hit["_source"]["shop_name"], hit["_source"]["badges"])
