# Need to run this file first before using the LineOA Webhook
from flask import Flask, request
app = Flask(__name__)
# Webhhook route for interact with KADMAN Account
# Will recieve the user ID from the webhook
@app.route('/webhook', methods=['POST'])
def webhook():
    body = request.json
    print("Webhook received!")
    for event in body['events']:
        user_id = event['source']['userId']
        print("User ID:", user_id)
    return 'OK', 200

if __name__ == '__main__':
    app.run(port=5000)
