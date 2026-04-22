"""
Job Application Routes
"""
from typing import Annotated, List, Any
from fastapi import (
    APIRouter,
    Depends,
    UploadFile,
    File,
    Form,
    BackgroundTasks,
    status,
    Query,
)
from sqlmodel import Session

from app.db.session import get_session
from app.core.utils import upload_cv_to_s3
from app.services.application import (
    create_application,
    get_employer_applications,
    get_top_candidates,
)
from app.services.ai_service import process_cv_with_ai
from app.api.v1.dependencies import CurrentUser, PaginationParams
from app.models.user import User
from app.core.logger import get_logger
from app.core.exceptions import BadRequestException, InternalServerErrorException

logger = get_logger(__name__)

app_router = APIRouter(tags=["Applications"])


@app_router.post(
    "/apply",
    status_code=status.HTTP_201_CREATED,
    summary="Submit a job application",
    description="Submit application with CV for a job posting (public endpoint)"
)
async def submit_application(
    background_tasks: BackgroundTasks,
    job_id: int = Form(..., description="Job ID"),
    applicant_email: str = Form(..., description="Applicant email"),
    applicant_phone: str = Form(..., description="Applicant phone"),
    file: UploadFile = File(..., description="CV file (PDF, DOC, DOCX)"),
    session: Session = Depends(get_session),
):
    """
    Submit a job application
    
    - **job_id**: ID of the job to apply for
    - **applicant_email**: Email address of the applicant
    - **applicant_phone**: Phone number of the applicant
    - **file**: CV file in PDF or Word format
    """
    # Upload CV to S3
    upload_result = upload_cv_to_s3(file, job_id)
    if not upload_result:
        logger.error(f"Failed to upload CV for job {job_id}")
        raise InternalServerErrorException(detail="Failed to upload CV")
    
    # Save application to database
    new_app = create_application(
        session=session,
        job_id=job_id,
        applicant_email=applicant_email,
        applicant_phone=applicant_phone,
        resume_url=upload_result["url"],
        cv_name=upload_result["cv_name"],
    )
    
    logger.info(f"Application submitted: {new_app.id} for job {job_id}")
    
    # Process CV with AI in background
    background_tasks.add_task(
        process_cv_with_ai,
        new_app.id,
        job_id,
        f"Applicant {applicant_email} with CV {upload_result['cv_name']}",
    )
    
    return {
        "success": True,
        "message": "Application submitted successfully!",
        "data": {
            "application_id": new_app.id,
            "cv_name": upload_result["cv_name"],
            "resume_url": upload_result["url"],
            "submitted_at": new_app.applied_at,
        }
    }


@app_router.get(
    "/employer/all",
    response_model=List[Any],
    status_code=status.HTTP_200_OK,
    summary="Get all applications for employer",
    description="Get all applications for jobs posted by the authenticated employer"
)
def list_employer_applications(
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
    pagination: PaginationParams,
):
    """Get all applications for employer's job postings"""
    applications = get_employer_applications(
        session=session,
        employer_id=current_user.id,
        skip=pagination.skip,
        limit=pagination.limit,
    )
    
    if not applications:
        logger.info(f"No applications found for employer {current_user.id}")
        return []
    
    logger.info(f"Retrieved {len(applications)} applications for employer {current_user.id}")
    return applications


@app_router.get(
    "/top-candidates",
    status_code=status.HTTP_200_OK,
    summary="Get top candidates",
    description="Get top candidates for jobs posted by the employer, filtered by AI score"
)
def get_top_candidates_endpoint(
    session: Annotated[Session, Depends(get_session)],
    current_user: CurrentUser,
    limit: Annotated[int, Query(ge=1, le=100, description="Max candidates to return")] = 10,
    min_score: Annotated[int, Query(ge=0, le=100, description="Minimum AI score filter")] = 0,
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
):
    """
    Get top candidates for employer
    
    Returns candidates ranked by AI score matching job requirements
    """
    # Calculate skip from page number
    skip = (page - 1) * limit
    
    candidates = get_top_candidates(
        session=session,
        recruiter_id=current_user.id,
        limit=limit,
        min_score=min_score,
        skip=skip,
    )
    
    logger.info(
        f"Retrieved top candidates for recruiter {current_user.id} "
        f"(limit={limit}, min_score={min_score})"
    )
    
    return {
        "success": True,
        "count": len(candidates),
        "filters": {
            "limit": limit,
            "min_score": min_score,
            "page": page,
        },
        "candidates": candidates,
    }
