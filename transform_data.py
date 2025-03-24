import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_class import RawTable, SearchCriteria, SearchResult, Qualification, Benefits, SkillsRequired


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

id="af979134-3340-4ed2-9426-f632795ec183"

raw_data =  session.query(RawTable).filter_by(search_criteria_id=id).first()
json_string =  json.loads(raw_data.raw_data)

# print(json_string)
for row in json_string:
    
    print(row["job title"], row["company"], row["job details"])

    data = SearchResult(
                date_search = row["date_search"],
                date_posted = row["date_posted"],
                html_string = None,
                is_processed = None,
                url_source = row["url_source"],
                search_criteria_id = id,
                qualification = [Qualification(
                    quality_description = row["job details"],
                    years_of_experience = None,
                    company_name = row["company"],
                    benefits = [Benefits(
                        benefits = row["job details"],                    
                        skillsrequired = [SkillsRequired(
                            skill = row["job details"] )]
                     )])])
                
                
    session.add(data)
    session.commit()
    session.refresh(data)
        