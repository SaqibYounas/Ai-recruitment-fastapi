from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session
from app.db.session import get_session
from app.services.s3_service import upload_file_to_s3
from app.models.application import JobApplication
from app.models.auth import User
from app.services.auth import get_current_user

app_router = APIRouter(prefix="/apply", tags=["Applications"])

@app_router.post("/")
async def apply_for_job(
    job_id: int = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # 1. File type check (optional but recommended)
    if file.content_type not in ["application/pdf", "application/msword"]:
        raise HTTPException(status_code=400, detail="Only PDF or Docx allowed")

    # 2. Upload to S3
    resume_url = upload_file_to_s3(file, current_user.id)
    
    if not resume_url:
        raise HTTPException(status_code=500, detail="Failed to upload resume to S3")

    # 3. Save to DB
    new_application = JobApplication(
        job_id=job_id,
        user_id=current_user.id,
        resume_url=resume_url
    )
    session.add(new_application)
    session.commit()
    
    return {"message": "Applied successfully", "resume_link": resume_url}