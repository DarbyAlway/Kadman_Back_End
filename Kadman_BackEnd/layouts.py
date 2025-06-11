from flask import Blueprint, jsonify, request
from db import wait_for_db_connection # Import db
import json 
from flask import Response
from mysql.connector import Error

layouts_bp = Blueprint('layouts', __name__) 
conn = wait_for_db_connection()

@layouts_bp.route("/show_all_layouts", methods=["GET"])
def show_all_layouts():
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM layouts")
        rows = cursor.fetchall()
        layouts = []
        for row in rows:
            layout = {
                "id": row[0],
                "name": row[1],
                "data": json.loads(row[2])
            }
            layouts.append(layout)
        cursor.close()
        return Response(
            json.dumps(layouts, ensure_ascii=False),
            content_type="application/json"
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/update_layout/<int:id>", methods=["PUT"])
def update_layout(id):
    try:
        data = request.get_json()

        layout_name = data.get("name")
        layout_data = data.get("data")

        if layout_name is None or layout_data is None:
            return jsonify({"error": "Missing 'name' or 'data'"}), 400

        # Convert layout_data to JSON string
        layout_data_str = json.dumps(layout_data, ensure_ascii=False)

        cursor = conn.cursor()
        cursor.execute(
            "UPDATE layouts SET name = %s, data = %s WHERE id = %s",
            (layout_name, layout_data_str, id)
        )
        conn.commit()
        cursor.close()

        return jsonify({"message": "Layout updated successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/insert_layout", methods=["POST"])
def insert_layout():
    try:
        data = request.get_json()

        layout_name = data.get("name")
        layout_data = data.get("data")

        if layout_name is None or layout_data is None:
            return jsonify({"error": "Missing 'name' or 'data'"}), 400

        # Convert layout_data to JSON string
        layout_data_str = json.dumps(layout_data, ensure_ascii=False)

        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO layouts (name, data) VALUES (%s, %s)",
            (layout_name, layout_data_str)
        )
        conn.commit()
        new_layout_id = cursor.lastrowid # Get the ID of the newly inserted row
        cursor.close()

        return jsonify({"message": "Layout added successfully", "id": new_layout_id}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@layouts_bp.route("/delete_layout/<int:id>", methods=["DELETE"])
def delete_layout(id):
    try:
        cursor = conn.cursor()
        
        # First, check if the layout exists
        cursor.execute("SELECT id FROM layouts WHERE id = %s", (id,))
        existing_layout = cursor.fetchone()

        if not existing_layout:
            cursor.close()
            return jsonify({"error": f"Layout with ID {id} not found"}), 404

        # If it exists, proceed with deletion
        cursor.execute("DELETE FROM layouts WHERE id = %s", (id,))
        conn.commit()
        cursor.close()

        return jsonify({"message": f"Layout with ID {id} deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
