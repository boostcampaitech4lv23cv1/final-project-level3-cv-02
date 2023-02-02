from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from db.session import Base

class Image_bundle(Base):
    __tablename__ = "IMAGE_BUNDLE"

    image_bundle_id = Column(String, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("USERS.user_id"))
    convert_time = Column(DateTime)
    convert_yn = Column(Boolean)