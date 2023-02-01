import bcrypt
import random
import string

def hashpw(pw: str):
    return bcrypt.hashpw(password=pw.encode('utf-8'), salt=bcrypt.gensalt())

def checkpw(inputpw: str, dbpw: str):
    return bcrypt.checkpw(inputpw.encode('utf-8'), dbpw.encode('utf-8'))

def randChar(num: int):
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(num))
