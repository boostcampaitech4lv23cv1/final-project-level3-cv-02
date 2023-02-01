from sqlalchemy.orm import Session
from typing import List
from db.schemas import image_bundle as image_bundle_schemas
from db.schemas import sound as sound_schemas
from db.models import sound as sound_model

#sound정보 생성
def create_sound(db: Session, sound:sound_schemas.Sound):
    new_sound = sound_model.Sound(
        image_bundle_id=sound.image_bundle_id,
        midi_url=sound.midi_url,
        mp3_url=sound.mp3_url
    )
    db.add(new_sound)
    db.commit()
    db.refresh(new_sound)
    return new_sound

#이미지번들ID로 sound정보 단건 조회
def get_sound_by_image_bundle_id(db: Session, id:image_bundle_schemas.ImageBundleBase):
    return db.query(sound_model.Sound)\
             .filter(sound_model.Sound.image_bundle_id == id).first()

#이미지번들ID 여러개로 sound정보 다건 조회
def get_sound_by_image_bundle_id(db: Session, ids:List[image_bundle_schemas.ImageBundleBase]):
    return list(db.query(sound_model.Sound)\
             .filter(sound_model.Sound.image_bundle_id.in_(ids)))