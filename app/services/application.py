"""
Job Application Services
"""
from sqlmodel import Session, select, desc
from typing import List, Optional

from app.models.application import JobApplication
from app.models.job import Job
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_application(
    session: Session,
    job_id: int,
    applicant_email: str,
    applicant_phone: str,
    resume_url: str,
    cv_name: str,
) -> JobApplication:
    """
    Create a new job application
    
    Args:
        session: Database session
        job_id: Job ID for application
        applicant_email: Applicant email
        applicant_phone: Applicant phone
        resume_url: URL to resume in S3
        cv_name: Name of CV file
        
    Returns:
        Created JobApplication object
    """
    try:
        new_app = JobApplication(
            job_id=job_id,
            applicant_email=applicant_email,
            applicant_phone=applicant_phone,
            resume_url=resume_url,
            cv_name=cv_name,
        )
        
        session.add(new_app)
        session.commit()
        session.refresh(new_app)
        
        logger.info(f"Application created: {new_app.id} for job {job_id}")
        return new_app
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating application: {str(e)}")
        raise


def get_employer_applications(
    session: Session,
    employer_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[dict]:
    """
    Get all applications for jobs posted by employer
    
    Args:
        session: Database session
        employer_id: Employer user ID
        skip: Number of records to skip
        limit: Number of records to return
        
    Returns:
        List of application dicts with job title
    """
    statement = (
        select(JobApplication, Job.title.label("job_title"))
        .join(Job, JobApplication.job_id == Job.id)
        .where(Job.user_id == employer_id)
        .offset(skip)
        .limit(limit)
        .order_by(JobApplication.applied_at.desc())
    )
    
    results = session.exec(statement).all()
    
    applications = []
    for app, job_title in results:
        app_data = {
            "id": app.id,
            "job_id": app.job_id,
            "job_title": job_title,
            "applicant_email": app.applicant_email,
            "applicant_phone": app.applicant_phone,
            "cv_name": app.cv_name,
            "resume_url": app.resume_url,
            "ai_score": app.ai_score or 0,
            "ai_summary": app.ai_summary,
            "status": app.status,
            "applied_at": app.applied_at,
        }
        applications.append(app_data)
    
    logger.info(f"Retrieved {len(applications)} applications for employer {employer_id}")
    return applications


def get_top_candidates(
    session: Session,
    recruiter_id: str,
    limit: int = 10,
    min_score: int = 0,
    skip: int = 0,
) -> List[dict]:
    """
    Get top candidates for jobs posted by recruiter
    
    Args:
        session: Database session
        recruiter_id: Recruiter user ID
        limit: Max number of candidates
        min_score: Minimum AI score filter
        skip: Number of records to skip
        
    Returns:
        List of top candidates sorted by AI score
    """
    statement = (
        select(JobApplication, Job.title)
        .join(Job, JobApplication.job_id == Job.id)
        .where(Job.user_id == recruiter_id)
        .where(JobApplication.ai_score >= min_score)
        .offset(skip)
        .limit(limit)
        .order_by(desc(JobApplication.ai_score))
    )
    
    results = session.exec(statement).all()
    
    candidates = [
        {
            "application_id": app.id,
            "job_id": app.job_id,
            "job_title": job_title,
            "applicant_email": app.applicant_email,
            "applicant_phone": app.applicant_phone,
            "cv_name": app.cv_name,
            "resume_url": app.resume_url,
            "ai_score": app.ai_score or 0,
            "ai_summary": app.ai_summary,
            "status": app.status,
            "applied_at": app.applied_at,
        }
        for app, job_title in results
    ]
    
    logger.info(
        f"Retrieved {len(candidates)} top candidates for recruiter {recruiter_id} "
        f"(min_score={min_score})"
    )
    return candidates


def update_application_score(
    session: Session,
    application_id: int,
    ai_score: int,
    ai_summary: Optional[str] = None,
) -> Optional[JobApplication]:
    """
    Update application AI score and summary
    
    Args:
        session: Database session
        application_id: Application ID
        ai_score: AI score (0-100)
        ai_summary: AI generated summary
        
    Returns:
        Updated application or None if not found
    """
    app = session.get(JobApplication, application_id)
    
    if not app:
        logger.warning(f"Application not found: {application_id}")
        return None
    
    try:
        app.ai_score = max(0, min(100, ai_score))  # Clamp between 0-100
        if ai_summary:
            app.ai_summary = ai_summary
        
        session.add(app)
        session.commit()
        session.refresh(app)
        
        logger.info(f"Application score updated: {application_id} (score={ai_score})")
        return app
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating application score: {str(e)}")
        raise


def update_application_status(
    session: Session,
    application_id: int,
    status: str,
) -> Optional[JobApplication]:
    """
    Update application status
    
    Args:
        session: Database session
        application_id: Application ID
        status: New status
        
    Returns:
        Updated application or None if not found
    """
    app = session.get(JobApplication, application_id)
    
    if not app:
        logger.warning(f"Application not found: {application_id}")
        return None
    
    try:
        app.status = status
        session.add(app)
        session.commit()
        session.refresh(app)
        
        logger.info(f"Application status updated: {application_id} (status={status})")
        return app
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating application status: {str(e)}")
        raise
