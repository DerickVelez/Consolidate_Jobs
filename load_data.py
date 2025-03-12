from sqlalchemy import create_engine, text, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
# from jobstreet_extract import scrape_jobstreet


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)
Base = declarative_base()


class MyTable(Base):
    __tablename__ = "raw_data_table"  # Must match the actual table name in the database
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    raw_data = Column(String, nullable=False)  # Ensure column names match exactly



SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)


# job_list = scrape_jobstreet("data engineer", "laguna")
test_data = 'something data'
data = MyTable(raw_data=test_data)
# jobs = [MyTable(raw_data=job) for job in job_list]

# Bulk insert into database
session.add(data)
session.commit()


with engine.connect() as connection:
    result = connection.execute(text("SELECT * FROM raw_data_table;"))
    
    
    rows = result.fetchall()
    for row in rows:
        print(row)
