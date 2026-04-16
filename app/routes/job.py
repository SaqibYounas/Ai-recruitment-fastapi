from fastapi import APIRouter, Depends, status
from sqlmodel import Session
from typing import Annotated, List
from app.db.session import get_session
from app.models.job import JobCreate, JobResponse
from app.models.auth import User
from app.services.jobs import create_new_job, get_all_jobs
from sqlmodel import Session, select

job_router = APIRouter(prefix="/jobs", tags=["Jobs"])

from fastapi import APIRouter, Depends, Request, status

@job_router.post("/", response_model=JobResponse)
def post_job(
    job_in: JobCreate, 
    request: Request, 
    session: Annotated[Session, Depends(get_session)]
):
    user_email = request.state.user_email
    
    user = session.exec(select(User).where(User.email == user_email)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # 3. User ID ke saath job create karein
    return create_new_job(job_data=job_in, session=session, user_id=user.id)

@job_router.get("/", response_model=List[JobResponse])
def list_jobs(session: Annotated[Session, Depends(get_session)]):
    return get_all_jobs(session)