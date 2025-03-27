from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, DateTime, func

from ...db.database import Base

import random, string

# pattern for photoid
def generate_photo_id():
    number_part = str(random.randint(1000,9999))
    letter_part = ''.join(random.choices(string.ascii_uppercase, k = 3))
    return "Photo" + number_part + letter_part
 
# Class model profilephoto with extended Base class
class ProfilePhoto(Base):
    __tablename__ = "profile_photo"

    Photo_ID = Column(String, primary_key=True, index=True, default=generate_photo_id)
    Photo_Url = Column(String, nullable=False)
    Photo_Type = Column(String, nullable = False)
    uploaded_at = Column(String, server_default=func.now(), onupdate=func.now(), nullable=False)

    # relationship with register (one to one)
    user_register = relationship("Register", back_populates="profile_photo", uselist=False)
   