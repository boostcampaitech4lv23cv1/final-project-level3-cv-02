from db.crud import users

def get_user_by_email(db, email):
    return users.get_user_by_email(db, email)