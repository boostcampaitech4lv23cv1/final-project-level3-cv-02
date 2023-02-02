import bcrypt
import random
import string
from PIL import Image 
import io
import os
from constant import paths
from db.session import bucket

def hashpw(pw: str):
    return bcrypt.hashpw(password=pw.encode('utf-8'), salt=bcrypt.gensalt())

def checkpw(inputpw: str, dbpw: str):
    return bcrypt.checkpw(inputpw.encode('utf-8'), dbpw.encode('utf-8'))

def randChar(num: int):
    return ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(num))

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