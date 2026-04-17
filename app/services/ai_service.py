import os
import json
import openai
from sqlmodel import select
from dotenv import load_dotenv
from app.models.job import Job 
from app.models.application import JobApplication

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

async def process_cv_with_ai(application_id: int, job_id: int, cv_text: str, session_factory):
    """
    Background Task: Job Description fetch karna, AI se score lena 
    aur Application table update karna.
    """
    with session_factory() as session:
        try:
            job_query = select(Job).where(Job.id == job_id)
            job_data = session.exec(job_query).first()
            
            if not job_data:
                print(f"Job ID {job_id} not found. Using default requirements.")
                job_requirements = "General technical skills, communication, and relevant experience."
            else:
                job_requirements = job_data.description

            prompt = f"""
            You are an AI Recruitment Specialist. Analyze the CV text against the Job Requirements.
            Provide a matching score (0-100) and a very brief summary.
            
            CRITICAL: Return ONLY a valid JSON object.
            Example Format: {{"score": 85, "summary": "Strong experience in React but lacks backend knowledge."}}
            
            Job Requirements:
            {job_requirements}
            
            CV Text:
            {cv_text}
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a helpful HR assistant that outputs JSON."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # AI ka response parse karein
            raw_content = response.choices[0].message.content
            ai_results = json.loads(raw_content)

            app_query = select(JobApplication).where(JobApplication.id == application_id)
            application = session.exec(app_query).first()

            if application:
                application.ai_score = ai_results.get("score", 0)
                application.ai_summary = ai_results.get("summary", "No summary provided.")
                application.cv_text = cv_text  # Store extracted text
                application.status = "completed"  # Mark as done
                
                session.add(application)
                session.commit()
                print(f"✅ AI Analysis completed for Application ID: {application_id}")
            else:
                print(f"❌ Application ID {application_id} not found in DB.")

        except Exception as e:
            print(f"⚠️ Error in AI Background Task: {str(e)}")
            # Error ki surat mein status failed kar dein taake frontend ko pata chal sake
            with session_factory() as error_session:
                app_err = error_session.get(JobApplication, application_id)
                if app_err:
                    app_err.status = "failed"
                    error_session.add(app_err)
                    error_session.commit()