from sqlmodel import Session, select
from app.models.job import Job, JobCreate
from typing import List

def create_new_job(job_data: JobCreate, session: Session, user_id: str, company_id: str):
    db_job = Job(
        **job_data.model_dump(), 
        user_id=user_id, 
        company_id=company_id
    )
    
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
        
    return db_job

def get_all_jobs(session: Session) -> List[Job]:
    statement = select(Job).where(Job.is_active == True) 
    results = session.exec(statement).all()
    
    return results