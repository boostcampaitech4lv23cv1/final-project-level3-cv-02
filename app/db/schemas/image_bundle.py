from typing import Optional, List
from pydantic import BaseModel
from db.models.image import Image

class ImageBundleBase(BaseModel):
    image_bundle_id: str

class ImageBundle(ImageBundleBase):
    user_id: int = 0
    convert_time: str
    convert_yn: bool
    image_urls: List

class ImageBundleCreate(ImageBundleBase):
    user_id: int = 0
    image_urls: List