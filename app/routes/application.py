from fastapi import APIRouter, Depends, UploadFile, File, Form, BackgroundTasks, Request,HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.core.utils import upload_cv_to_s3
from app.services.application import save_application_to_db
from app.services.ai_service import process_cv_with_ai

app_router = APIRouter(prefix="/apply", tags=["Applications"])

@app_router.post("/")
async def apply_for_job(
    background_tasks: BackgroundTasks,
    request: Request,
    job_id: int = Form(...),
    applicant_email: str = Form(...), 
    applicant_phone: str = Form(...), 
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    user_id = getattr(request.state, "user_id", "1") 

    resume_url = upload_cv_to_s3(file, job_id)
    if not resume_url:
        raise HTTPException(status_code=500, detail="S3 Upload Failed")


    new_app = save_application_to_db(
        session=session,
        job_id=job_id,
        user_id=user_id,
        applicant_email=applicant_email,
        applicant_phone=applicant_phone,
        resume_url=resume_url,
    )
    cv_content = f"Applicant {applicant_email} skills for Job {job_id}" 

    background_tasks.add_task(
        process_cv_with_ai, 
        new_app.id, 
        job_id, 
        cv_content, 
    )

    return {
        "message": "Application submitted! Our AI is analyzing your CV.",
        "application_id": new_app.id
    }
