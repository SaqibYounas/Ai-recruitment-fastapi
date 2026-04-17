from pypdf import PdfReader
import requests
from io import BytesIO
import boto3
from fastapi import UploadFile
from app.core.settings import settings

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

def upload_cv_to_s3(file: UploadFile, job_id: int):
    bucket_name = settings.AWS_BUCKET_NAME
    file_key = f"resumes/job_{job_id}/{file.filename}"
    
    try:
        s3_client.upload_fileobj(
            file.file,
            bucket_name,
            file_key,
            ExtraArgs={
                "ContentType": file.content_type,
            }
        )
        return f"https://{bucket_name}.s3.{'ap-south-1'}.amazonaws.com/{file_key}"
    except Exception as e:
        print(f"S3 Upload Error: {e}")
        return None