from flask import Flask, request
from dotenv import load_dotenv
import os
import requests
from db import wait_for_db_connection
app = Flask(__name__)
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_KEY') 
conn = wait_for_db_connection()

@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    for event in body['events']:
        if event['type'] =='follow':
            user_id = event['source']['userId']
            user_profile = get_user_profile(user_id)
            print("Webhook received!")
            print("New User Followed:", user_id)
            insert_waiting_vendor(user_id, user_profile)
    return 'OK', 200


def get_user_profile(user_id):
    headers = {
        "Authorization": f"Bearer {CHANNEL_ACCESS_TOKEN}"
    }
    url = f"https://api.line.me/v2/bot/profile/{user_id}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to get user profile:", response.text)

def insert_waiting_vendor(user_id, user_profile):
    cursor = conn.cursor()
    display_name = user_profile.get('displayName', '') if user_profile else ''
    sql = "INSERT INTO waiting_vendors (LineID, UserProfile) VALUES (%s, %s)"
    cursor.execute(sql, (user_id, display_name))
    conn.commit()
    cursor.close()
    print(f"Inserted waiting vendor: {user_id}, DisplayName: {display_name}")


if __name__ == '__main__':
    app.run(port=5000)
