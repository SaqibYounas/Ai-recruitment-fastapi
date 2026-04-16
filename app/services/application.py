# import boto3
# from botocore.exceptions import NoCredentialsError
# from fastapi import UploadFile
# import os

# AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")

# s3_client = boto3.client(
#     's3',
#     aws_access_key_id=AWS_ACCESS_KEY,
#     aws_secret_access_key=AWS_SECRET_KEY
# )

# def upload_file_to_s3(file: UploadFile, user_id: int):
#     file_extension = file.filename.split(".")[-1]
#     s3_file_path = f"resumes/user_{user_id}_{file.filename}"
    
#     try:
#         s3_client.upload_fileobj(
#             file.file,
#             BUCKET_NAME,
#             s3_file_path,
#             ExtraArgs={"ContentType": file.content_type}
#         )
#         # S3 URL generate karein
#         file_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{s3_file_path}"
#         return file_url
#     except Exception as e:
#         print(f"S3 Upload Error: {e}")
#         return None