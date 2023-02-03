from pydantic import BaseModel
from typing import Optional

class Sound(BaseModel):
    sound_id: int
    image_bundle_id: str
    midi_url: str
    mp3_url: str

class SoundCreate(BaseModel):
    image_bundle_id: str
    midi_url: Optional[str]
    mp3_url: str