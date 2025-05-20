from elasticsearch import Elasticsearch
import os
from flask import Flask, request, jsonify,Response
from pythainlp.tokenize import syllable_tokenize

app = Flask(__name__)
import json
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', 'Z_3O+lFyJPcXxPB+UvD-')),  # Using environment variable for security
    ca_certs=os.path.expanduser("~/http_ca.crt")  # Ensure the path is correct
)

INDEX_NAME = "kadman"  

@app.route("/search", methods=["GET"])
def search():
    query_text = request.args.get("q", "")
    if not query_text:
        return jsonify({"error": "Missing query parameter 'q'"}), 400

    query_syllables = syllable_tokenize(query_text)

    query_body = {
    "query": {
        "bool": {
            "should": [
                {
                    "multi_match": {
                        "query": query_text,
                        "fields": ["shop_name", "badges"]
                    }
                },
                {
                    "terms": {
                        "shop_name_syllables": query_syllables
                    }
                }
            ]
        }
     }
    }

    try:
        result = es.search(index=INDEX_NAME, body=query_body, size=100)
        hits = result.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]

        # Use Response with json.dumps and ensure_ascii=False
        return Response(
            json.dumps({"results": results}, ensure_ascii=False),
            content_type="application/json"
        )
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/search_all", methods=["GET"])
def search_all():
    query_text = request.args.get("q", "")

    if not query_text:
        query_body = {"query": {"match_all": {}}}
    else:
        query_body = {
            "query": {
                "multi_match": {
                    "query": query_text,
                    "fields": ["vendorID", "shop_name", "badges"]  # all fields you want to search
                }
            }
        }

    try:
        result = es.search(index=INDEX_NAME, body=query_body, size=100)
        hits = result.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]

        # Use Response with json.dumps and ensure_ascii=False
        return Response(
            json.dumps({"results": results}, ensure_ascii=False),
            content_type="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)