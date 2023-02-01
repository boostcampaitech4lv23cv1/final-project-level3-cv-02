import bcrypt
import random
import string

def hashpw(pw: str):
    return bcrypt.hashpw(password=pw, salt=bcrypt.gensalt())

def checkpw(inputpw: str, dbpw: str):
    return bcrypt.checkpw(inputpw, dbpw)

def randChar(num: int):
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(num))
