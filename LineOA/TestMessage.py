import requests
from dotenv import load_dotenv
import os
load_dotenv()
CHANNEL_ACCESS_TOKEN = os.getenv('LineOA_KEY') 
# Replace this with your actual Channel Access Token

# List of user IDs (must have sent a message to your LINE OA)
user_ids = [
    'U187b91a5499f71fc6bd043862859c15a',
    'Uba9c6372c95976bb909ebce81e86b933'
    ]

message = {
    "type": "text",
    "text": "พี่จ๋าน้ำจะแตก"
}

url = 'https://api.line.me/v2/bot/message/multicast'

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {CHANNEL_ACCESS_TOKEN}'
}

payload = {
    "to": user_ids,
    "messages": [message]
}

response = requests.post(url, headers=headers, json=payload)

print(f'Status Code: {response.status_code}')
print(response.text)