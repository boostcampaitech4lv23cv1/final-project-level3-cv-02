from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from db.session import Base

class Sound(Base):
    __tablename__ = "SOUND"
    
    sound_id = Column(Integer, primary_key=True, index=True)
    image_bundle_id = Column(String, ForeignKey("IMAGE_BUNDLE.image_bundle_id"))
    midi_url = Column(String)
    mp3_url = Column(String)

    image_bundle = relationship("Image_bundle", back_populates="SOUND")