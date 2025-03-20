from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from create_class import SearchCriteria, RawTable
from jobstreet_extract import scrape_jobstreet


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)
Base = declarative_base()



SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)


def insert_raw_data(keyword, location):
    session = SessionLocal()
    
    try: 
        
        result = scrape_jobstreet(keyword, location)
        
        data = SearchCriteria(
            keyword = keyword,
            location = location,
            rawtable = [RawTable(
                raw_data = result
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

insert_raw_data("industrial engineer", 'laguna') 

# # job_list = scrape_jobstree/t("data engineer", "laguna")
# test_data = 'something data'
# data = MyTable(raw_data=test_data)
# # jobs = [MyTable(raw_data=job) for job in job_list]

# # Bulk insert into database
# session.add(data)
# session.commit()


# with engine.connect() as connection:
#     result = connection.execute(text("SELECT * FROM raw_data_table;"))
    
    
#     rows = result.fetchall()
#     for row in rows:
#         print(row)
