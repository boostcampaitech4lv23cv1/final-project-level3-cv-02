from pydantic import BaseModel

class Image(BaseModel):
    sound_id: int
    image_bundle_id: str
    midi_url: str
    mp3_url: str