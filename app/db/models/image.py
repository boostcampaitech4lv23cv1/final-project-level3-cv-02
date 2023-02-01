from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base

class Image(Base):
    __tablename__ = "IMAGE"
    
    image_id = Column(Integer, primary_key=True, index=True)
    image_bundle_id = Column(String, ForeignKey("IMAGE_BUNDLE.image_bundle_id"))
    image_url = Column(String)

    image_bundle = relationship("Image_bundle", back_populates="IMAGE")