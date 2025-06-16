from flask import Blueprint, jsonify, request
from db import get_db_connection
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

# Update vendors badges
@vendors_bp.route("/update_badges",methods=["POST"])
def update_badges():
    conn = get_db_connection()
    try:
        cursor = conn.cursor()

        data = request.get_json()
        vendorID = data.get("vendorID")
        badge_name = data.get("badges")  # this is already a Python list
        shop_name = data.get("shop_name")

        # Save to MySQL
        sql = "UPDATE vendors SET badges = %s WHERE vendorID = %s"
        badge_json = json.dumps(badge_name, ensure_ascii=False)
        cursor.execute(sql, (badge_json, vendorID))
        print(f"Rows affected: {cursor.rowcount}")
        conn.commit()
        cursor.close()
        print(type(badge_name))
        es.update(
            index=INDEX_NAME,
            id=vendorID,
            body={
                "doc": {
                    "shop_name":shop_name,
                    "badges": badge_name,  # not badge_json
                    "shop_name_syllables": syllable_tokenize(shop_name)
                }
            }
        )
        print(badge_name)
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
        result = es.search(index=INDEX_NAME, body=query_body, size=200)
        hits = result.get("hits", {}).get("hits", [])
        results = [hit["_source"] for hit in hits]
        results = sorted(results, key=lambda x: x.get("vendorID"))
        return Response(
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# return all vendors info from the database
@vendors_bp.route("/get_all_vendors", methods=["GET"])
def get_all_vendors():
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM vendors") #Query to get all vendors
        results = cursor.fetchall()

        cursor.close()
        conn.close()

        return Response(
            json.dumps(results, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Delete selected badges from a vendors table
@vendors_bp.route("/delete_selected_badges", methods=["POST"])
def delete_selected_badges():
    conn = get_db_connection()
    try:
        data = request.get_json()
        vendorID = data.get("vendorID")
        badges_to_remove = data.get("badges")  # list of badges to remove

        if not vendorID or not isinstance(badges_to_remove, list):
            return jsonify({"error": "vendorID and list of badges are required"}), 400

        cursor = conn.cursor()

        # Get current badges
        cursor.execute("SELECT badges FROM vendors WHERE vendorID = %s", (vendorID,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Vendor not found"}), 404

        current_badges = json.loads(result[0]) if result[0] else []

        # Filter out the badges to remove
        updated_badges = [b for b in current_badges if b not in badges_to_remove]
        updated_json = json.dumps(updated_badges, ensure_ascii=False)

        # Update the DB
        cursor.execute("UPDATE vendors SET badges = %s WHERE vendorID = %s", (updated_json, vendorID))
        conn.commit()
        cursor.close()
 # Re-index this vendor in Elasticsearch with updated badges

        es.index(
            index=INDEX_NAME,
            id=vendorID,  # Use vendorID as the document ID
            body={
                "vendorID": vendorID,
                "badges": updated_badges,
            }
        )

        return jsonify({"message": "Selected badges removed", "badges left": updated_badges}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Add a new vendors to the database
@vendors_bp.route("/add_vendors", methods=["POST"])
def add_vendors():
    conn = get_db_connection()
    try:
        data = request.get_json()
        shop_name = data.get("shop_name")
        badges = data.get("badges")

        badge_json = json.dumps(badges, ensure_ascii=False) if badges else None
        cursor = conn.cursor()
        sql = "INSERT INTO vendors (shop_name, badges) VALUES (%s, %s)"
        cursor.execute(sql, (shop_name, badge_json))
        vendor_id = cursor.lastrowid  # Get the last inserted vendor ID
        print("New vendor ID:", vendor_id)
        conn.commit()
        cursor.close()

        # Indexing new vendor in Elasticsearch
        es.index(
            index=INDEX_NAME,
            id = vendor_id,
            body={
                "vendorID": vendor_id,
                "shop_name": shop_name,
                "badges": badges,
                "shop_name_syllables": syllable_tokenize(shop_name)
            }
        )

        return jsonify({"message": "Vendor added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500