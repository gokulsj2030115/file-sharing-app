import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    S3_BUCKET = os.environ.get('S3_BUCKET', 'filesharing-proj-asia')
    S3_REGION = os.environ.get('S3_REGION', 'ap-south-1')
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-123')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB limit
