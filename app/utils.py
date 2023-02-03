import bcrypt
import random
import string
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


from PIL import Image 
import io
import os
from constant import paths
from db.session import bucket

try:
    from secret import ID, TOKEN
except:
    print("예외가 발생했습니다. secret.py를 만들어 Gmail ID, PWD를 명시하세요.")

def hashpw(pw: str):
    return bcrypt.hashpw(password=pw.encode('iso-8859-1'), salt=bcrypt.gensalt())

def checkpw(inputpw: str, dbpw: str):
    return bcrypt.checkpw(inputpw.encode('utf-8'), dbpw.encode('utf-8'))

def randChar(num: int):
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(num))

def send_email(address: str) -> str:
    rand_number = "".join([str(random.randint(0,9)) for _ in range(6)])
    sender_email = ID 
    receiver_email = address
    password = TOKEN 
    
    message = MIMEMultipart("alternative")
    message["Subject"] = f"Maestro 회원가입 인증용 번호는 {rand_number}입니다."
    message["From"] = sender_email 
    message["To"] = receiver_email  
    
    html = f"""
    <h1> 안녕하세요, 고객님! <h1>
    <h2> Maestro 서비스를 이용해주셔서 감사합니다.</h2>
    <div class="check">
      <h2 class="display1"> Email Verification</h2>
      <div class="display2">
        <h4 class="text"> 인증용 번호는 {rand_number}입니다.</h4>
        <h4 class="text"> 5분안에 번호를 입력해주세요!</h4>
      </div>
    """
    
    html_part = MIMEText(html, "html")
    message.attach(html_part)
    context = ssl.create_default_context()
    print("메일을 보내는 중입니다...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
    
    return rand_number
def save_images(images, id):
    IMAGE_PATH = os.path.join(paths['img_path'], id)
    os.makedirs(IMAGE_PATH)

    for order, image_file in enumerate(images):
        image = Image.open(io.BytesIO(image_file.file.read()))
        file_name = f"{IMAGE_PATH}/{order}_{image_file.filename}"
        image.save(file_name)
        print(f"{id}/{image_file.filename} 저장되었습니다.")
    return [(f"{IMAGE_PATH}/{fname}", fname) for fname in os.listdir(IMAGE_PATH)]

def upload_files(file_paths, type, id):
    paths = []
    for path, name in file_paths:
        print(path)
        file_name = os.path.join(type, f"{id}/{name}")
        blob = bucket.blob(file_name)
        blob.upload_from_filename(path)
        paths.append(file_name)
    return paths
