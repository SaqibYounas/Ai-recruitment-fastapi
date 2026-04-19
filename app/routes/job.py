from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from typing import Annotated, List
from app.db.session import get_session
from app.models.job import  JobCreate, JobResponse
from app.models.user import User
from app.services.jobs import create_new_job, get_all_jobs
from app.core.security import verify_token 

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])

@job_router.post("/", response_model=JobResponse)
def post_job(
    job_in: JobCreate, 
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(verify_token)] 
):
    
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")

    return create_new_job(
        job_data=job_in, 
        session=session, 
        user_id=current_user.id,
        company_id=current_user.company_id
    )

@job_router.get("/all", response_model=List[JobResponse])
def list_jobs(session: Annotated[Session, Depends(get_session)]):
    return get_all_jobs(session)