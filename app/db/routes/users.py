from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.connection import get_db
from db.service import users as users_service
from db.schemas import users as users_schema

router = APIRouter(
    prefix="/users", # url 앞에 고정적으로 붙는 경로추가
)

'''
유저 신규 생성
이메일, 패스워드 필요
'''
@router.post("/")
def create_user(db: Session = Depends(get_db), user:users_schema.UserCreate=None):
    res = users_service.create_user(db, user)
    return {"res": res}

'''
유저 이메일로 유저 단건 조회
이메일 필요
'''
@router.get("/")
def get_user_by_email(db: Session = Depends(get_db), email='unkwon@unkwon.com'):
    res = users_service.get_user_by_email(db, email)
    return {"res": res}

'''
유저 패스워드 변경
이메일, 패스워드, 새 패스워드 필요.
기존 패스워드 틀릴 시 error 발생.
'''
@router.put("/")
def update_passwd(db: Session = Depends(get_db), user:users_schema.UserPasswdUpdate=None):
    users_service.update_passwd(db, user)


'''
유저 삭제
이메일, 패스워드 필요.
패스워드 틀릴 시 error 발생
'''
@router.delete("/")
def delete_user_by_email(db: Session = Depends(get_db), user:users_schema.UserDelete=None):
    users_service.delete_user_by_email(db, user)