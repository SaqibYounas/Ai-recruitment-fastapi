from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Request, HTTPException
from sqlmodel import Session
from typing import Annotated, List, Any
from app.db.session import get_session
from app.core.utils import upload_cv_to_s3
from app.services.application import save_application_to_db, get_applications_for_employer
from app.services.ai_service import process_cv_with_ai
from app.core.security import verify_token
from app.models.user import User

app_router = APIRouter(prefix="/applications", tags=["Applications"])

@app_router.post("/apply")
async def apply_for_job(
    background_tasks: BackgroundTasks,
    job_id: int = Form(...),
    applicant_email: str = Form(...), 
    applicant_phone: str = Form(...), 
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    
    upload_result = upload_cv_to_s3(file, job_id,)
    if not upload_result:
        raise HTTPException(status_code=500, detail="S3 Upload Failed")

    new_app = save_application_to_db(
        session=session,
        job_id=job_id,
        applicant_email=applicant_email,
        applicant_phone=applicant_phone,
        resume_url=upload_result["url"],
        cv_name=upload_result["cv_name"]
    )

    background_tasks.add_task(
        process_cv_with_ai, 
        new_app.id, 
        job_id, 
        f"Applicant {applicant_email} with CV {upload_result['cv_name']}", 
    )

    return {
        "message": "Application submitted successfully!",
        "application_id": new_app.id,
        "cv_name": upload_result["cv_name"],
        "resume_url": upload_result["url"]
    }

@app_router.get("/employer/all", response_model=List[Any])
def list_employer_applications(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(verify_token)]
):
    applications = get_applications_for_employer(session, current_user.id)
    
    if not applications:
        return []

    return applications