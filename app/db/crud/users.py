from sqlalchemy.orm import Session
from db.schemas import users as users_schemas
from db.models import users as users_model

def get_user_by_email(db: Session, email: str):
    return db.query(users_model.Users)\
             .filter(users_model.Users.user_email == email).first()