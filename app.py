from elasticsearch import Elasticsearch
import os
from flask import Flask, request, jsonify,Response
from pythainlp.tokenize import syllable_tokenize
from dotenv import load_dotenv
import json
import re


app = Flask(__name__)
load_dotenv()
ES_KEY = os.getenv('ES_KEY') 
print("ES_KEY:", ES_KEY)
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', ES_KEY)),
    ca_certs=os.path.expanduser("~/http_ca.crt")  # Ensure the path is correct
)

INDEX_NAME = "kadman"  

@app.route("/search", methods=["GET"])
def search():
    query_text = request.args.get("q", "")
    cleaned_query = re.sub(r'["\'\s]+', '', query_text)


    if cleaned_query and cleaned_query != "":
        query_syllables = syllable_tokenize(cleaned_query)
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "multi_match": {
                                "query": cleaned_query,
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
        print(f"Query text: '{cleaned_query}'")
        print(f"Query body: {json.dumps(query_body, ensure_ascii=False)}")
    else:
        # Match all documents when query is empty
        query_body = {
            "query": {
                "match_all": {}
            }
        }
     

    try:
        result = es.search(index=INDEX_NAME, body=query_body, size=100)
        hits = result.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]

        return Response(
            json.dumps({"results": results}, ensure_ascii=False),
            content_type="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


if __name__ == "__main__":
    app.run(debug=True)