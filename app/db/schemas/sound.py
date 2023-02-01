from pydantic import BaseModel

class SoundBase(BaseModel):
    sound_id: int
    
class Sound(SoundBase):
    image_bundle_id: str
    midi_url: str
    mp3_url: str