from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base # Base 생성
from db.core.config import settings
from constant import BUCKET_NAME
from google.cloud import storage
from google.oauth2 import service_account

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL
engine = create_engine(SQLALCHEMY_DATABASE_URL)

Session = sessionmaker(autocommit=False,autoflush=False,bind=engine)
Base = declarative_base()

KEY_PATH = 'db/core/key.json'
credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
client = storage.Client(credentials = credentials, project = credentials.project_id)

# 버킷 객체 생성
bucket = client.bucket(BUCKET_NAME)