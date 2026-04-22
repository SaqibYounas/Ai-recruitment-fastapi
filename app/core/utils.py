"""
Utility Functions for PDF Processing and S3 Upload
"""
from pypdf import PdfReader
import requests
from io import BytesIO
import boto3
from fastapi import UploadFile
from app.core.settings import settings
from app.core.logger import get_logger
import time

logger = get_logger(__name__)

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name=settings.AWS_REGION,
)


async def extract_text_from_s3_url(url: str) -> str:
    """
    Extract text from PDF file in S3
    
    Args:
        url: S3 URL of PDF file
        
    Returns:
        Extracted text from PDF
    """
    try:
        logger.info(f"Extracting text from S3: {url}")
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        reader = PdfReader(BytesIO(response.content))
        text = ""
        
        for page_num, page in enumerate(reader.pages):
            try:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
            except Exception as e:
                logger.warning(f"Error extracting page {page_num}: {str(e)}")
                continue
        
        logger.info(f"Successfully extracted text from PDF ({len(text)} chars)")
        return text.strip()
        
    except requests.RequestException as e:
        logger.error(f"Error downloading PDF from S3: {str(e)}")
        return ""
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {str(e)}")
        return ""


def upload_cv_to_s3(file: UploadFile, job_id: int) -> dict | None:
    """
    Upload CV file to S3
    
    Args:
        file: Uploaded file
        job_id: Associated job ID
        
    Returns:
        Dict with 'url' and 'cv_name' or None if failed
    """
    bucket_name = settings.AWS_BUCKET_NAME
    
    try:
        # Validate file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset to start
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            logger.warning(f"File too large: {file_size} bytes")
            return None
        
        # Create unique filename
        timestamp = int(time.time())
        unique_filename = f"{timestamp}_{file.filename}"
        file_key = f"resumes/job_{job_id}/{unique_filename}"
        
        logger.info(f"Uploading CV to S3: {file_key}")
        
        # Upload to S3
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file_key,
            ExtraArgs={
                "ContentType": file.content_type,
            }
        )
        
        # Generate S3 URL
        url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        
        logger.info(f"CV uploaded successfully: {url}")
        return {"url": url, "cv_name": unique_filename}
        
    except Exception as e:
        logger.error(f"S3 upload error: {str(e)}", exc_info=True)
        return None

