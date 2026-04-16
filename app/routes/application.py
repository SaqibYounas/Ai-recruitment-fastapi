from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Request
from sqlmodel import Session
from app.db.session import get_session
from app.core.utils import upload_cv_to_s3
from app.services.application import save_application_to_db, 
import uuid

router = APIRouter(prefix="/apply", tags=["Applications"])

@router.post("/")
async def apply_for_job(
    request: Request,
    job_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    user_id = getattr(request.state, "user_id", str(uuid.uuid4())) 
    resume_url = upload_cv_to_s3(file, job_id)
    
    if not resume_url:
        return {"error": "Failed to upload CV to S3"}

    application = save_application_to_db(
        session=session, 
        job_id=job_id, 
        user_id=user_id, 
        resume_url=resume_url
    )

    return {
        "message": "Application submitted successfully!",
        "application_id": application.id,
        "resume_url": resume_url
    }