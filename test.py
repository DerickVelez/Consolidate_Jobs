import json
import re
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_class import RawTable, SearchCriteria, SearchResult, Qualification, Benefits, SkillsRequired



DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def load_overall_data(search_criteria_id):
    raw_data =  session.query(RawTable).filter_by(search_criteria_id=search_criteria_id).first()
    json_string =  json.loads(raw_data.raw_data)
    
    job =[]
    
    for row in json_string:
        while len(job) < 2:
            cleaned_job = re.sub(r"[\xa0\n\r\t]", ";", row['job_details']) 
            job.append(cleaned_job)
           
            
    return job

result = load_overall_data("fd7fd8c5-937c-4edf-bb19-8fa6fcebf252")

clean_text = re.sub(r"[\xa0\n\r\t]", ";", result[-2])  
print(clean_text)

