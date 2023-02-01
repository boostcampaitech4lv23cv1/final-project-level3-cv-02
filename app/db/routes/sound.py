from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.connection import get_db

router = APIRouter(
    prefix="/sound", # url 앞에 고정적으로 붙는 경로추가
)