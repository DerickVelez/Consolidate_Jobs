import re
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from job_details_extractor import get_job_details
from sqlalchemy.orm import sessionmaker
from create_class import AIResponse ,RawTable, SearchResult, Qualification, Benefits, SkillsRequired, create_engine


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)



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

result = get_job_details("6e6215fa-7faf-4884-b38d-f5a23cdd02e4")

clean_text = re.sub(r"[\xa0\n\r\t]", ";", result[-2])  

payload = {f'message: {clean_text}'}
headers = {"Content-Type": "application/json"}


# response = session.get(url,  headers=headers)
response = requests.post(url, json=payload, headers=headers)

print(response.status_code)
print(response.json())

processed_data = response.json()

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

data = RawTable(
    airesponse = [AIResponse(
        response = processed_data
    )]
)

session.add(data)
session.commit(data)