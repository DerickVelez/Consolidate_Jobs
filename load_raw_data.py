import json
from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from create_class import SearchCriteria, RawTable
from jobstreet_extract import find_job


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)
Base = declarative_base()



SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)


def insert_raw_data(keyword, location):
    session = SessionLocal()
    
    try: 
        
        result = find_job(keyword, location)
        json_result = json.dumps(result,indent=4) 
        
        data = SearchCriteria(
            keyword = keyword,
            location = location,
            rawtable = [RawTable(
                raw_data = json_result
            )]
            
        )
            
        session.add(data)
        session.commit()
        session.refresh(data)
        
    except Exception as e:
        session.rollback()
        print(f'Error inserting data: {e}')
    finally: 
        session.close()

insert_raw_data("data engineer", 'laguna') 
