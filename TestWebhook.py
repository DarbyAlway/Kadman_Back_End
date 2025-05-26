import requests

url = 'https://a876-2001-fb1-105-f3de-b873-f928-e053-8fc8.ngrok-free.app/webhook'
payload = {
    "events": [
        {
            "source": {
                "userId": "U1234567890"
            }
        }
    ]
}

response = requests.post(url, json=payload)
print(response.status_code)
print(response.text)
 