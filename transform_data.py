from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_class import RawTable, SearchCriteria


DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

search_criteria_query = session.query(SearchCriteria).filter_by(
    id = "6f7f11f5-88f6-410a-89aa-2d0fd49ab7a9"
    
).first()

raw_data =  session.query(RawTable).filter_by(
    search_criteria_id=search_criteria_query.id
).first()


test_string = raw_data.raw_data


start_string = "Clicking job"
end_string = "Report jobCancel"

# start_index = test_string.find(start_string)
# end_index = test_string.find(end_string,start_index)


# if start_index != -1 and end_index != 1:
#     substring = test_string[len(start_string) + start_index:end_index]
# print(substring)


jobs = []
start_index = 0
job_counter = 0
while True:
    start_index = test_string.find(start_string, start_index)
    if start_index == -1:
        break  

    start_index += len(start_string)  # Move index past starter
    end_index = test_string.find(end_string, start_index)
    job_counter += 1
    

    if end_index == -1:
        break  

    output = f'{job_counter} {test_string[start_index:end_index].strip()}'# Extract substring
    jobs.append(output)
    start_index = end_index + len(end_string) 
    
print(jobs)

with open( r'D:\development\python\JOB_WEB_SCRAPING\drafts\raw_output1.txt', 'w', encoding='utf-8') as file:
     file.writelines("\n".join(jobs))  # Write all jobs properly

    
    