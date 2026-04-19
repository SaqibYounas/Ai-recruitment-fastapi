from sqlmodel import Session, select, desc
from app.models.application import JobApplication
from app.models.job import Job
from typing import List

def save_application_to_db(
    session: Session, 
    job_id: int, 
    applicant_email: str, 
    applicant_phone: str, 
    resume_url: str, 
    cv_name: str
):
    new_app = JobApplication(
        job_id=job_id,
        applicant_email=applicant_email,
        applicant_phone=applicant_phone,
        resume_url=resume_url,
        cv_name=cv_name
    )
    session.add(new_app)
    session.commit()
    session.refresh(new_app)
    return new_app

def get_applications_for_employer(session: Session, employer_id: str):
    statement = (
        select(JobApplication, Job.title.label("job_title"))
        .join(Job, JobApplication.job_id == Job.id)
        .where(Job.user_id == employer_id)
    )
    results = session.exec(statement).all()
    
    final_data = []
    for app, job_title in results:
        data = app.model_dump()
        data["job_title"] = job_title
        final_data.append(data)
    return final_data


def get_filtered_recruiter_data(session: Session, recruiter_id: str, limit: int, min_score: int):
    statement = (
        select(JobApplication, Job.title)
        .join(Job, JobApplication.job_id == Job.id)
        .where(Job.user_id == recruiter_id)       
        .where(JobApplication.ai_score >= min_score) 
        .order_by(desc(JobApplication.ai_score))     
        .limit(limit)                              
    )
    
    results = session.exec(statement).all()
    
    return [
        {
            "application_id": app.id,
            "job_title": job_title,
            "applicant_email": app.applicant_email,
            "applicant_phone": app.applicant_phone,
            "cv_name": app.cv_name,
            "resume_url": app.resume_url,
            "ai_score": app.ai_score,
            "status": app.status,
            "applied_at": app.applied_at
        }
        for app, job_title in results
    ]