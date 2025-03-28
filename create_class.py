import uuid
from sqlalchemy import create_engine, text, Column, Integer, String, ForeignKey, DateTime, Boolean, JSON
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID  



DB_URL = "postgresql://postgres:Workeye29@localhost:5432/alljobs"
engine = create_engine(DB_URL, pool_reset_on_return=None)

Base = declarative_base()


class SearchCriteria(Base):
    __tablename__ = "search_criteria"   
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    keyword = Column(String, nullable=False)
    location = Column(String, nullable=True)   
    
    rawtable = relationship("RawTable", back_populates="searchcriteria", cascade="all, delete-orphan")
    searchresult = relationship("SearchResult", back_populates="searchcriteria", cascade="all, delete-orphan")

class RawTable(Base):
    __tablename__ = "raw_data_table" 
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    search_criteria_id = Column(UUID(as_uuid=True), ForeignKey('search_criteria.id'), nullable=False)    
    raw_data = Column(JSON)  
 
    searchcriteria = relationship("SearchCriteria", back_populates="rawtable")


class SearchResult(Base):
    __tablename__="search_result"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    date_search = Column(DateTime, nullable=False)
    date_posted = Column(DateTime)
    html_string = Column(String, nullable=True)
    is_processed = Column(Boolean, nullable=True)
    url_source = Column(String)
    job_responsibility = Column(String)
    search_criteria_id = Column(UUID(as_uuid=True), ForeignKey('search_criteria.id'), nullable=False)
    
    searchcriteria = relationship("SearchCriteria", back_populates="searchresult")
    qualification = relationship("Qualification", back_populates="searchresult", cascade="all, delete-orphan")
    
class Qualification(Base):
    __tablename__="qualification"
    
    id = Column(Integer, primary_key=True)
    qualification = Column(String)
    years_of_experience = Column(Integer)
    company_name = Column(String, nullable=False)
    search_result_id = Column(UUID(as_uuid=True), ForeignKey('search_result.id'), nullable=False)
    
    searchresult = relationship("SearchResult", back_populates="qualification")
    benefits = relationship("Benefits", back_populates="qualification", cascade="all, delete-orphan")
    
class Benefits(Base):
    __tablename__="benefits"
    
    id = Column(Integer, primary_key=True)
    benefits = Column(String)
    qualification_id = Column(Integer, ForeignKey('qualification.id'))
    
    qualification = relationship("Qualification", back_populates="benefits")
    skillsrequired = relationship("SkillsRequired", back_populates="benefits", cascade="all, delete-orphan")
    
class SkillsRequired(Base):
    __tablename__='skills_required'
    
    id = Column(Integer, primary_key=True)
    skill = Column(String)
    benefits_id = Column(Integer, ForeignKey('benefits.id'))

    benefits =  relationship("Benefits", back_populates="skillsrequired")

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()

Base.metadata.create_all(engine)

#no salaary on the schema add salaryyy!!