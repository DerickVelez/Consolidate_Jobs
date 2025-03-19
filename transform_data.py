from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_class import RawTable, SearchCriteria


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

search_criteria_query = session.query(SearchCriteria).filter_by(
    id= 3
).first()

raw_data =  session.query(RawTable).filter_by(
    search_criteria_id=search_criteria_query.id
).first()

print
print(raw_data.raw_data)

starter = "Return to search resultsModify my search"
ender = "Report jobCancel"

