from flask import Blueprint, jsonify, request
from db import get_connection # Import db
import json 
from pythainlp.tokenize import syllable_tokenize
from elasticsearch import Elasticsearch
import re
import os
from dotenv import load_dotenv
from flask import Response

vendors_bp = Blueprint('vendors', __name__)# Vendors Blueprint
load_dotenv()  # Load environment variables from .env file
ES_KEY = os.getenv('ES_KEY')
es = Elasticsearch(
    "https://localhost:9200",
    basic_auth=("elastic", os.getenv('ELASTIC_PASSWORD', ES_KEY)),
    ca_certs=os.path.expanduser("~/http_ca.crt") 
)
INDEX_NAME = "kadman"  
conn = get_connection()  # Get database connection

# Update vendors badges
@vendors_bp.route("/update_badges",methods=["POST"])
def update_badges():
    try:
        cursor = conn.cursor()

        # Get json from request
        data = request.get_json()
        vendorID = data.get("vendorID")
        badge_name = data.get("badges")
        badge_json = json.dumps(badge_name, ensure_ascii=False)
        
        print("vendors:", vendorID, badge_json)
        sql = "UPDATE vendors SET badges = %s WHERE vendorID = %s"
        cursor.execute(sql, (badge_json, vendorID))
        conn.commit()
        cursor.close()
        return jsonify({"message": "Badges added successfully"}), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# Search for vendors
@vendors_bp.route("/search", methods=["GET"])
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
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# return all vendors info from the database
@vendors_bp.route("/get_all_vendors", methods=["GET"])
def get_all_vendors():
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vendors")
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return Response(
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500