import json
from sqlalchemy.orm import declarative_base, sessionmaker
from create_class import SearchCriteria, RawTable, create_engine
from jobstreet_extract import find_job


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)
Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)

def insert_raw_data(keyword, location):
    session = SessionLocal()
    
    try: 
        result = find_job(keyword, location)  # Should be a list of dicts
        jobs = json.dumps(result, indent=4)
        
        for item in result:
            job_details_raw = item.get('job_details', "")

            if isinstance(job_details_raw, str):
                job_details_list = job_details_raw.split('\n')
            elif isinstance(job_details_raw, list):
                job_details_list = job_details_raw
            else:
                job_details_list = []

            data = SearchCriteria(
                keyword=keyword,
                location=location,
                rawtable=[
                    RawTable(
                        raw_data= jobs,
                        job_details=job_details_list
                    )
                ]
            )
        session.add(data)
        session.commit()    
        session.refresh(data)
        # print(json_parsed['job_details'])
        
    except Exception as e:
        session.rollback()
        
        print(f'Error inserting data: {e}')
    finally: 
        session.close()

insert_raw_data("airline", 'cavite') 
