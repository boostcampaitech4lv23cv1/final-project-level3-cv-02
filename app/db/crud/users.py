from sqlalchemy.orm import Session
from db.schemas import users as users_schemas
from db.models import users as users_model
from utils import hashpw, checkpw

#유저 신규 생성
def create_user(db: Session, user:users_schemas.UserCreate):
    hashed_passwd = hashpw(user.user_password)
    new_user = users_model.Users(user_email=user.user_email, user_password=hashed_passwd, auth_yn=False)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

#유저 이메일로 유저 단건 조회
def get_user_by_email(db: Session, email: str):
    return db.query(users_model.Users)\
             .filter(users_model.Users.user_email == email).first()

#유저 패스워드 변경
def update_passwd(db: Session, user:users_schemas.UserPasswdUpdate):
    db_user = get_user_by_email(db, user.user_email)
    if checkpw(user.user_password, db_user.user_password) == False:
        raise Exception('비밀번호가 다릅니다.')

    db_user.update({"user_password": hashpw(user.new_password)})
    db.commit()
    return db_user

#유저 정보 삭제
def delete_user_by_email(db:Session, user: users_schemas.UserDelete):
    db_user = get_user_by_email(db, user.user_email)
    if checkpw(user.user_password, db_user.user_password) == False:
        raise Exception('비밀번호가 다릅니다.')

    db_user.delete({"user_password": hashpw(user.new_password)})
    db.commit()