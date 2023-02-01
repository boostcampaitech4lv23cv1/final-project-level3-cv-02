from typing import Optional, List
from pydantic import BaseModel
from db.models.image import Image

class ImageBundleBase(BaseModel):
    image_bundle_id: str

class ImageBundle(ImageBundleBase):
    user_id: int
    convert_time: str
    convert_yn: bool
    images: List[Image] = []

class ImageBundleCreate(ImageBundleBase):
    user_id: int
    images: List[Image] = []