from sqlmodel import Session, select
from app.models.job import Job, JobCreate
from typing import List, Dict, Any

def create_new_job(job_data: JobCreate, session: Session, user_id: str):
    db_job = Job(**job_data.model_dump(), user_id=user_id)
    session.add(db_job)
    session.commit()
    session.refresh(db_job)
    
    frontend_base_url = "https://your-portal.com/apply" 
    link = f"{frontend_base_url}/{db_job.id}"
    
    db_job_dict = db_job.model_dump()
    db_job_dict["shareable_link"] = link
    
    return db_job_dict

def get_all_jobs(session: Session) -> List[Job]:
    statement = select(Job).where(Job.is_active == True) 
    results = session.exec(statement)
    return results.all()