from elasticsearch import Elasticsearch, helpers
import json
import os
from pythainlp.tokenize import syllable_tokenize

es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', 'Z_3O+lFyJPcXxPB+UvD-')),
    ca_certs=os.path.expanduser("~/http_ca.crt")
)

index_name = "kadman"

if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name)
    print("Old index deleted.")

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
                "type": "keyword"  # store syllable tokens exactly
            },
            "badges": {"type": "keyword"}
        }
    }
}

es.indices.create(index=index_name, body=index_body)
print(f"Index '{index_name}' created with Thai analyzer.")

with open("vendors.json", "r", encoding="utf-8") as f:
    vendors = json.load(f)

# Tokenize shop_name to syllables
for vendor in vendors:
    shop_name = vendor.get("shop_name", "")
    syllables = syllable_tokenize(shop_name)
    vendor["shop_name_syllables"] = syllables

actions = [
    {
        "_index": index_name,
        "_id": vendor["vendorID"],
        "_source": vendor
    }
    for vendor in vendors
]

helpers.bulk(es, actions)

res = es.search(index=index_name, body={"query": {"match_all": {}}}, size=10)
for hit in res["hits"]["hits"]:
    print(json.dumps(hit["_source"], ensure_ascii=False, indent=2))

print('Indexing completed.')
