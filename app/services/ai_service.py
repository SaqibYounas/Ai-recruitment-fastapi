"""
AI Service for CV Processing and Analysis
"""
import json
from typing import Optional
import openai
from sqlmodel import select

from app.models.job import Job
from app.models.application import JobApplication
from app.core.settings import settings
from app.config.dbconnection import SessionLocal
from app.core.logger import get_logger

logger = get_logger(__name__)

# Set OpenAI API key
openai.api_key = settings.OPENAI_API_KEY


async def process_cv_with_ai(
    application_id: int,
    job_id: int,
    cv_text: str,
) -> Optional[JobApplication]:
    """
    Process CV with AI for analysis and scoring
    
    Uses OpenAI to analyze CV against job requirements
    
    Args:
        application_id: Application ID
        job_id: Job ID
        cv_text: CV text content
        
    Returns:
        Updated application object or None
    """
    with SessionLocal() as session:
        try:
            # Get job details
            job_query = select(Job).where(Job.id == job_id)
            job = session.exec(job_query).first()
            
            if not job:
                logger.warning(f"Job not found: {job_id}")
                return None
            
            job_requirements = job.description
            
            logger.info(f"Processing CV with AI: application_id={application_id}, job_id={job_id}")
            
            # Create prompt for AI analysis
            prompt = f"""
            Analyze the CV against Job Requirements.
            Return ONLY a JSON object with:
            - 'score' (0-100 integer): How well the CV matches the requirements
            - 'summary' (string, max 2 sentences): Brief summary of key matches
            
            Job Requirements: {job_requirements}
            
            CV Text: {cv_text}
            """
            
            # Call OpenAI API
            try:
                response = openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an HR assistant that provides JSON responses with CV analysis."
                        },
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,  # Lower temperature for consistency
                )
                
                # Parse AI response
                ai_results = json.loads(response.choices[0].message.content)
                
                logger.info(f"AI analysis completed: score={ai_results.get('score')}")
                
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response as JSON: {str(e)}")
                ai_results = {"score": 0, "summary": "Analysis failed"}
            except Exception as e:
                logger.error(f"OpenAI API error: {str(e)}")
                raise
            
            # Update application with AI results
            app_query = select(JobApplication).where(JobApplication.id == application_id)
            application = session.exec(app_query).first()
            
            if not application:
                logger.warning(f"Application not found: {application_id}")
                return None
            
            # Set AI analysis results
            application.ai_score = min(100, max(0, ai_results.get("score", 0)))  # Clamp 0-100
            application.ai_summary = ai_results.get("summary", "")
            application.cv_text = cv_text
            application.status = "analyzed"
            
            session.add(application)
            session.commit()
            session.refresh(application)
            
            logger.info(f"Application updated with AI results: {application_id}")
            return application
            
        except Exception as e:
            logger.error(f"Error processing CV with AI: {str(e)}", exc_info=True)
            return None


async def extract_cv_text_from_url(url: str) -> Optional[str]:
    """
    Extract text from CV URL
    
    Args:
        url: CV URL (typically from S3)
        
    Returns:
        Extracted text or None
    """
    from app.core.utils import extract_text_from_s3_url
    
    try:
        logger.info(f"Extracting CV text from URL: {url}")
        text = await extract_text_from_s3_url(url)
        logger.info(f"Successfully extracted {len(text)} characters")
        return text
    except Exception as e:
        logger.error(f"Error extracting CV text: {str(e)}")
        return None