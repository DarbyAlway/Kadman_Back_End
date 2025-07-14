import mysql.connector
from elasticsearch import Elasticsearch, helpers
from pythainlp.tokenize import syllable_tokenize
import os
import json
from dotenv import load_dotenv
# Step 1: Connect to AWS Aurora (MySQL-compatible)
conn = mysql.connector.connect(
    host="kadman-database.c8boumioc8hx.us-east-1.rds.amazonaws.com",
    user="admin",
    password="12345678",
    database="kadmandb",
    port=3306
)
load_dotenv() 
cursor = conn.cursor(dictionary=True)  # So it returns rows as dicts
ES_KEY = os.getenv('ES_KEY')

# Step 2: Query vendor data
cursor.execute("SELECT vendorID, shop_name, badges FROM vendors")
vendors = cursor.fetchall()

# Step 3: Connect to Elasticsearch
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', ES_KEY)),
    ca_certs=os.path.expanduser("~/http_ca.crt")
)

index_name = "kadman"

# Step 4: (Optional) Delete old index
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print("Old index deleted.")

# Step 5: Create index with custom Thai analyzer
index_body = {
    "settings": {
        "analysis": {
            "tokenizer": {
                "edge_ngram_thai": {
                    "type": "edge_ngram",
                    "min_gram": 2,
                    "max_gram": 20,
                    "token_chars": ["letter", "digit"]
                }
            },
            "analyzer": {
                "thai_autocomplete": {
                    "type": "custom",
                    "tokenizer": "edge_ngram_thai",
                    "filter": ["lowercase"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "vendorID": {"type": "keyword"},
            "shop_name": {
                "type": "text",
                "analyzer": "thai_autocomplete",
                "search_analyzer": "thai_autocomplete"
            },
            "shop_name_syllables": {
                "type": "keyword"
            },
            "badges": {"type": "keyword"}
        }
    }
}

es.indices.create(index=index_name, body=index_body)
print(f"Index '{index_name}' created with Thai analyzer.")

# Step 6: Parse badges JSON string to list and tokenize shop_name
for vendor in vendors:
    # Parse badges field from JSON string to Python list
    badges_str = vendor.get("badges")
    if badges_str:
        try:
            vendor["badges"] = json.loads(badges_str)
        except json.JSONDecodeError:
            vendor["badges"] = []  # fallback to empty list if parsing fails

    # Tokenize shop_name into syllables
    shop_name = vendor.get("shop_name", "")
    vendor["shop_name_syllables"] = syllable_tokenize(shop_name)

# Prepare bulk actions
actions = [
    {
        "_index": index_name,
        "_id": vendor["vendorID"],
        "_source": vendor
    }
    for vendor in vendors
]
# Step 7: Bulk index into Elasticsearch
helpers.bulk(es, actions)
print("Data indexed directly from Aurora to Elasticsearch.")

# Step 8: Sample query
res = es.search(index=index_name, body={"query": {"match_all": {}}}, size=10)
for hit in res["hits"]["hits"]:
    print(hit["_source"])

# Cleanup
cursor.close()
conn.close()
