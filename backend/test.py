import requests 
import json

BASE = "http://127.0.0.1:5000"

headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
data = json.dumps({"url": None})

response2 = requests.post(BASE + "/get-url-from-frontend", data=data, headers=headers)
print(response2.json())

response1 = requests.get(BASE + "/check-url-status")
print(response1.json())
