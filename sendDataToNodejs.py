import requests
import json
url = "http://192.168.0.69:3000/data"

data = {
    "sensor_id": "1234",
    "temperature": 22.5,
    "humidity": 45.3
}

# HTTP hlavicka
headers = {"Content-Type":"application/json"}

#Odesilani dat
try:
    response = requests.post(url, data=json.dumps(data), headers=headers)
    print(f"Server responed with status: {response.status_code}")
    print(response.text)
except Exception as e:
    print(f"Failed to send data: {e}")