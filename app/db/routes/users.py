from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.connection import get_db
from db.service import users

router = APIRouter(
    prefix="/users", # url 앞에 고정적으로 붙는 경로추가
)

@router.get("/")
def get_user_by_email(db: Session = Depends(get_db), email='unkwon@unkwon.com'):
    res = users.get_user_by_email(db, email)
    return {"res": res}