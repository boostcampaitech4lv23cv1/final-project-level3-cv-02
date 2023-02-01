from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship
from db.session import Base

class Users(Base):
    __tablename__ = "USERS"

    user_id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String, unique=True, index=True)
    user_password = Column(String)
    auth_yn = Column(Boolean)

    image_bundle = relationship("Image_bundle", back_populates="USERS")