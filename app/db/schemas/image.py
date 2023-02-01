from pydantic import BaseModel

class Image(BaseModel):
    image_id: int
    image_bundle_id: str
    image_url: str