import requests

url = ""

payload = {""}

headers = {
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.status_code)  
print(response.json())        