import os
import json
import openai
from sqlmodel import select
from app.models.job import Job 
from app.models.application import JobApplication
from app.core.settings import settings
from app.config.dbconnection import SessionLocal

openai.api_key = settings.OPENAI_API_KEY

async def process_cv_with_ai(application_id: int, job_id: int, cv_text: str):
    with SessionLocal() as session:
        try:
            job_query = select(Job).where(Job.id == job_id)
            job_data = session.exec(job_query).first()
             
            job_requirements = job_data.description if job_data else "General technical skills and experience."

            prompt = f"""
            Analyze the CV against Job Requirements.
            Return ONLY a JSON object with 'score' (0-100) and 'summary' (max 2 sentences).
            
            Requirements: {job_requirements}
            CV Text: {cv_text}
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an HR assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            ai_results = json.loads(response.choices[0].message.content)

            app_query = select(JobApplication).where(JobApplication.id == application_id)
            application = session.exec(app_query).first()

            if application:
                application.ai_score = ai_results.get("score", 0)
                application.ai_summary = ai_results.get("summary", "")
                application.cv_text = cv_text
                application.status = "completed"
                
                session.add(application)
                session.commit()
                print(f"Success: {application_id}")

        except Exception as e:
            print(f"Error: {str(e)}")
            session.rollback()
            try:
                app_err = session.get(JobApplication, application_id)
                if app_err:
                    app_err.status = "failed"
                    session.add(app_err)
                    session.commit()
            except:
                pass