"""
Job Services
"""
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime

from app.models.job import Job, JobCreate
from app.core.logger import get_logger

logger = get_logger(__name__)


def create_job(
    job_data: JobCreate,
    session: Session,
    user_id: str,
    company_id: str,
) -> Job:
    """
    Create a new job posting
    
    Args:
        job_data: Job creation data
        session: Database session
        user_id: Creator user ID
        company_id: Associated company ID
        
    Returns:
        Created job object
    """
    try:
        db_job = Job(
            **job_data.model_dump(),
            user_id=user_id,
            company_id=company_id,
        )
        
        session.add(db_job)
        session.commit()
        session.refresh(db_job)
        
        logger.info(f"Job created: {db_job.id} by user {user_id}")
        return db_job
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error creating job: {str(e)}")
        raise


def get_all_jobs_paginated(
    session: Session,
    skip: int = 0,
    limit: int = 20,
    is_active: bool = True,
) -> List[Job]:
    """
    Get all active jobs with pagination
    
    Args:
        session: Database session
        skip: Number of records to skip
        limit: Number of records to return
        is_active: Filter by active status
        
    Returns:
        List of job objects
    """
    statement = select(Job).where(
        Job.is_active == is_active
    ).offset(skip).limit(limit).order_by(Job.created_at.desc())
    
    jobs = session.exec(statement).all()
    logger.info(f"Retrieved {len(jobs)} jobs (skip={skip}, limit={limit})")
    
    return jobs


def get_user_jobs(
    session: Session,
    user_id: str,
    skip: int = 0,
    limit: int = 20,
) -> List[Job]:
    """
    Get jobs created by specific user
    
    Args:
        session: Database session
        user_id: User ID to filter by
        skip: Number of records to skip
        limit: Number of records to return
        
    Returns:
        List of job objects
    """
    statement = select(Job).where(
        Job.user_id == user_id
    ).offset(skip).limit(limit).order_by(Job.created_at.desc())
    
    jobs = session.exec(statement).all()
    logger.info(f"Retrieved {len(jobs)} jobs for user {user_id}")
    
    return jobs


def get_job_by_shareable_id(session: Session, shareable_id: str) -> Optional[Job]:
    """
    Get job by shareable ID
    
    Args:
        session: Database session
        shareable_id: Shareable ID of the job
        
    Returns:
        Job object or None if not found
    """
    statement = select(Job).where(Job.shareable_id == shareable_id)
    job = session.exec(statement).one_or_none()
    
    return job


def update_job(
    session: Session,
    job_id: int,
    user_id: str,
    job_data: dict,
) -> Optional[Job]:
    """
    Update job posting
    
    Args:
        session: Database session
        job_id: Job ID to update
        user_id: User ID (for authorization check)
        job_data: Updated job data
        
    Returns:
        Updated job object or None if not found
    """
    job = session.get(Job, job_id)
    
    if not job:
        logger.warning(f"Job not found: {job_id}")
        return None
    
    if job.user_id != user_id:
        logger.warning(f"Unauthorized update attempt for job {job_id} by user {user_id}")
        return None
    
    try:
        for key, value in job_data.items():
            if value is not None:
                setattr(job, key, value)
        
        job.updated_at = datetime.utcnow()
        session.add(job)
        session.commit()
        session.refresh(job)
        
        logger.info(f"Job updated: {job_id}")
        return job
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error updating job: {str(e)}")
        raise


def delete_job(session: Session, job_id: int, user_id: str) -> bool:
    """
    Delete job posting
    
    Args:
        session: Database session
        job_id: Job ID to delete
        user_id: User ID (for authorization check)
        
    Returns:
        True if deleted, False otherwise
    """
    job = session.get(Job, job_id)
    
    if not job:
        logger.warning(f"Job not found: {job_id}")
        return False
    
    if job.user_id != user_id:
        logger.warning(f"Unauthorized delete attempt for job {job_id} by user {user_id}")
        return False
    
    try:
        session.delete(job)
        session.commit()
        
        logger.info(f"Job deleted: {job_id}")
        return True
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error deleting job: {str(e)}")
        raise
