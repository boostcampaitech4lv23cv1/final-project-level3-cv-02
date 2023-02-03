from utils import upload_files
from db.crud import sound
from db.schemas import sound as sound_schemas
from constant import paths
from constant import BUCKET_URL

def upload_sound(db, image_bundle_id):
    
    path = upload_files([(f"{paths['mp3_path']}/{image_bundle_id}/result_0.mp3", "result_0.mp3")]
                        , "sound", image_bundle_id)
    mp3_url = BUCKET_URL+path[0]
    
    sound.create_sound(db, sound_schemas.SoundCreate(image_bundle_id=image_bundle_id, 
                        mp3_url=mp3_url))
    return mp3_url