# from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
# from sqlmodel import Session
# from app.db.session import get_session
# from app.services.application import upload_file_to_s3
# from app.models.application import JobApplication
# from app.models.auth import User
# from app.services.auth import get_current_user
# from fastapi import BackgroundTasks
# from app.core.utils import extract_text_from_url
# from app.services.ai_services import analyze_candidate
# import json
# app_router = APIRouter(prefix="/apply", tags=["Applications"])


# @app_router.post("/")
# async def apply_for_job(
#     job_id: int = Form(...),
#     file: UploadFile = File(...),
#     session: Session = Depends(get_session),
#     current_user: User = Depends(get_current_user)
# ):
#     # 1. S3 Upload (Jo pehle kiya tha)
#     resume_url = upload_file_to_s3(file, current_user.id)
    
#     # 2. Get Job Description
#     job = session.get(Job, job_id)
    
#     # 3. AI Analysis
#     cv_text = await extract_text_from_url(resume_url)
#     ai_result_raw = analyze_candidate(job.description, cv_text)
#     ai_data = json.loads(ai_result_raw)

#     # 4. Save to DB with AI Score
#     new_application = JobApplication(
#         job_id=job_id,
#         user_id=current_user.id,
#         resume_url=resume_url,
#         ai_score=ai_data['score'],
#         ai_analysis=ai_data['reason']
#     )
#     session.add(new_application)
#     session.commit()
    
#     return {
#         "message": "Applied and AI Analyzed", 
#         "score": ai_data['score'], 
#         "analysis": ai_data['reason']
#     }