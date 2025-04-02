import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter

url = "https://job-api.alvinalmodal.dev/job-api-requests"

retries = Retry(
    total= 5,
    backoff_factor=2,
    status_forcelist=[
        429,
        500,
        502,
        503,
        504
    ]
)

adapter = HTTPAdapter(max_retries=retries)

session = requests.Session()
session.mount("http://", adapter)
session.mount("https://", adapter)


# payload = {
#   "userId": 1,
#   "id": 1,
#   "title": "Mama mo",
#   "completed": False
# }

headers = {
    "Content-Type": "application/json"
}




response = session.get(url,  headers=headers)
# response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())



# response = requests.get(url)

# if response.status_code == 200:  # Check if request was successful
#     data = response.json()  # Convert response to JSON
#     print(data)
# else:
#     print(f"Error: {response.status_code}")