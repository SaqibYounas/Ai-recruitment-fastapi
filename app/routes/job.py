"""
Job Routes
"""
from typing import Annotated, List
from fastapi import APIRouter, Depends, status, Query
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.job import Job, JobCreate, JobResponse
from app.models.user import User
from app.api.v1.dependencies import CurrentUser, PaginationParams
from app.services.jobs import create_job, get_all_jobs_paginated, get_user_jobs
from app.core.logger import get_logger

logger = get_logger(__name__)

job_router = APIRouter(tags=["Jobs"])


@job_router.post(
    "/",
    response_model=JobResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new job posting",
    description="Create a new job posting (requires authentication and company info)"
)
def create_new_job(
    job_in: JobCreate,
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
):
    """Create a new job posting"""
    if not current_user.company_id:
        from app.core.exceptions import BadRequestException
        raise BadRequestException(
            detail="Please add company information before creating a job posting"
        )
    
    job = create_job(
        job_data=job_in,
        session=session,
        user_id=current_user.id,
        company_id=current_user.company_id,
    )
    
    logger.info(f"Job created by user {current_user.id}: {job.id}")
    return job


@job_router.get(
    "/",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="Get user's job postings",
    description="Get all job postings created by the current user"
)
def list_user_jobs(
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
    pagination: PaginationParams,
):
    """Get all job postings created by the current user"""
    jobs = get_user_jobs(
        session=session,
        user_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    
    return jobs


@job_router.get(
    "/all",
    response_model=List[JobResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all active job postings",
    description="Get all active job postings (public endpoint, no authentication required)"
)
def list_all_jobs(
    session: Annotated[Session, Depends(get_session)],
    pagination: PaginationParams,
    is_active: Annotated[bool, Query(description="Filter by active status")] = True,
):
    """
    Get all active job postings
    
    This is a public endpoint that returns all active job postings.
    """
    jobs = get_all_jobs_paginated(
        session=session,
        skip=pagination.skip,
        limit=pagination.limit,
        is_active=is_active,
    )
    
    return jobs
