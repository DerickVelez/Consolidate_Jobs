import json
from sqlalchemy.orm import sessionmaker
from create_class import RawTable, SearchResult, Qualification, Benefits, SkillsRequired, create_engine


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

def load_overall_data(search_criteria_id):
    raw_data =  session.query(RawTable).filter_by(search_criteria_id=search_criteria_id).first()
    json_string =  json.loads(raw_data.raw_data)

    for row in json_string:
        job_details = repr(row["job_details"]).replace("\n", ";")

        data = SearchResult(
                    date_search = row["date_search"],
                    date_posted = row["date_posted"],
                    html_string = None,
                    is_processed = True,    
                    job_responsibility = job_details,
                    url_source = row["url_source"],
                    search_criteria_id = search_criteria_id,
                    qualification = [Qualification( 
                        qualification = job_details,
                        years_of_experience = None,
                        company_name = row["company"],
                        benefits = [Benefits(
                            benefits = job_details,                    
                            skillsrequired = [SkillsRequired(
                                skill = job_details )]
                        )])])
                    
        session.add(data)
        session.commit()
        session.refresh(data)
        
load_overall_data("be8ffe30-ef58-421e-8569-4c2c3eba1f02")