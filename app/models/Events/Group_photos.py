from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ...db.database import Base

import random, string

# Function to generate a unique Group ID
def generate_group_id():
    number_part = str(random.randint(1000, 9999))
    letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))
    return "Group" + number_part + letter_part

# Model for storing group photos
class Group_Photos(Base):
    __tablename__ = "Group_Photos_Table"

    # Unique Group ID
    GID = Column(String, primary_key=True, index=True, default=generate_group_id)
    
    # URL of the uploaded photo
    Photo_Url = Column(String, nullable=True)
    
    # Timestamp for when the photo was uploaded or updated
    Uploaded_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationship with Event model
    events = relationship("Event", back_populates="group_photos", uselist=False)
