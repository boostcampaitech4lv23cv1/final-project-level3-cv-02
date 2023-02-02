from typing import List
from sqlalchemy.orm import Session
from db.schemas import image_bundle as image_bundle_schemas
from db.models import image_bundle as image_bundle_model
from db.models import image as image_model
from datetime import datetime
from utils import randChar

#이미지번들 생성
def create_image_bundle(db: Session, img_bdl:image_bundle_schemas.ImageBundleCreate):

    now = datetime.now()
    new_img_bdl = image_bundle_model.Image_bundle(
        image_bundle_id=img_bdl.image_bundle_id,
        user_id=img_bdl.user_id,
        convert_time=now,
        convert_yn=False
    )
    db.add(new_img_bdl)
    db.commit()

    __create_images(db, img_bdl.image_bundle_id, img_bdl.image_urls)

    db.refresh(new_img_bdl)
    return new_img_bdl

#이미지번들ID로 이미지번들 단건 조회
def get_image_bundle_by_id(db: Session, id: str):
    return db.query(image_bundle_model.Image_bundle)\
             .filter(image_bundle_model.Image_bundle.image_bundle_id == id).first()

#유저 id로 이미지번들 다건 조회
def get_image_bundle_by_user_id(db: Session, user_id: str):
    return list(db.query(image_bundle_model.Image_bundle)\
             .filter(image_bundle_model.Image_bundle.user_id == user_id))


'''image 관련 crud'''
#image 정보 생성(타 서비스에서 호출x)
def __create_images(db: Session, image_bundle_id:str, urls:List[str]):
    new_images = [image_model.Image(
        image_bundle_id=image_bundle_id,
        image_url=url
    ) for url in urls]
    db.add_all(new_images) #add_all : 오류 시 전부 롤백
    db.commit()

#이미지번들ID로 image 정보 다건 조회
def get_image_by_image_bundle_id(db: Session, image_bundle_id:str):
    return list(db.query(image_model.Image)\
             .filter(image_model.Image.image_bundle_id == image_bundle_id))