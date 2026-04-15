from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Annotated, List
from app.db.session import get_session
from app.models.job import JobCreate, JobResponse
from app.models.auth import User
from app.services.auth import get_current_user
from app.services.jobs import create_new_job, get_all_jobs

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])

@job_router.post("/", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def post_job(
    job_in: JobCreate, 
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    return create_new_job(job_data=job_in, session=session, current_user=current_user)

@job_router.get("/", response_model=List[JobResponse])
def list_jobs(session: Annotated[Session, Depends(get_session)]):
    return get_all_jobs(session)