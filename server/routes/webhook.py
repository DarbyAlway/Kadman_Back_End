import os
import requests
import mysql.connector
from flask import Blueprint, request
from dotenv import load_dotenv
from db import get_db_connection

load_dotenv()

webhook_bp = Blueprint('webhook', __name__)

CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_Key')


@webhook_bp.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    for event in body['events']:
        if event['type'] == 'follow':
            user_id = event['source']['userId']
            user_profile = _get_user_profile(user_id)
            _insert_waiting_vendor(user_id, user_profile)
    return 'OK', 200


def _get_user_profile(user_id):
    response = requests.get(
        f"https://api.line.me/v2/bot/profile/{user_id}",
        headers={"Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"}
    )
    return response.json() if response.status_code == 200 else None


def _insert_waiting_vendor(user_id, user_profile):
    conn = get_db_connection()
    cursor = conn.cursor()
    display_name = user_profile.get('displayName', '') if user_profile else ''
    try:
        cursor.execute(
            "INSERT INTO waiting_vendors (LineID, UserProfile) VALUES (%s, %s)",
            (user_id, display_name)
        )
        conn.commit()
    except mysql.connector.errors.IntegrityError as err:
        if err.errno != 1062:
            raise
    finally:
        cursor.close()
        conn.close()
