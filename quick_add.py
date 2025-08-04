import requests
import json

# Dane pracownika
data = {
    "id": "mptaszkowski",
    "first_name": "Michał",
    "last_name": "Ptaszkowski",
    "hourly_rate": 25.0,
    "pin": "1111"
}

# Wyślij POST
response = requests.post("http://127.0.0.1:8000/workers", json=data)
print(f"Status: {response.status_code}")
print(f"Response: {response.text}")
