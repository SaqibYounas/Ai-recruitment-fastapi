from pypdf import PdfReader
import requests
from io import BytesIO
import boto3
from fastapi import UploadFile
from app.core.settings import settings
import time

s3_client = boto3.client(
    "s3",
    aws_access_key_id='',
    aws_secret_access_key='',
    region_name=settings.AWS_REGION
)

async def extract_text_from_s3_url(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status() 
        
        reader = PdfReader(BytesIO(response.content))
        text = ""
        
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
                
        return text.strip()
    except Exception as e:
        print(f"Extraction Error: {e}")
        return "" 

def upload_cv_to_s3(file: UploadFile, job_id: int, user_id: str):
    bucket_name = settings.AWS_BUCKET_NAME
    
    timestamp = int(time.time())
    unique_filename = f"{timestamp}_{file.filename}"
    
    file_key = f"resumes/user_{user_id}/job_{job_id}/{unique_filename}"
    
    try:
        file.file.seek(0)
        
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file_key,
            ExtraArgs={
                "ContentType": file.content_type,
            }
        )
        url = f"https://{bucket_name}.s3.{settings.AWS_REGION}.amazonaws.com/{file_key}"
        return {"url": url, "cv_name": unique_filename}
        
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None
