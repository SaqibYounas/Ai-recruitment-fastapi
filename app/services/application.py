from sqlmodel import Session
from app.models.application import JobApplication

def save_application_to_db(
    session: Session, 
    job_id: int, 
    user_id: str, 
    resume_url: str,
    applicant_email: str, 
    applicant_phone: str 
):
    new_application = JobApplication(
        job_id=job_id,
        user_id=user_id,
        resume_url=resume_url,
        applicant_email=applicant_email,
        applicant_phone=applicant_phone, 
        status="pending"
    )
    
    session.add(new_application)
    session.commit()
    session.refresh(new_application)
    return new_application