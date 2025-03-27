from sqlalchemy import Column, String, DateTime, func, ForeignKey
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from ...db.database import Base
import random, string

# Function to generate a unique Event Photo ID
def generate_id():
    number_part = str(random.randint(1000, 9999))  # Generate a 4-digit random number
    letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))  # Generate 3 random uppercase letters
    return "EPhoto_ID" + number_part + letter_part

# Event_Photos Model Definition
class Event_Photos(Base):
    __tablename__ = "EventPhotos"

    # Primary Key: Unique Event Photo ID
    Event_Photos_ID = Column(String, primary_key=True, default=generate_id)
    
    # Foreign Key referencing Events table
    Event_ID = Column(String, ForeignKey("Events.Event_ID", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    
    # User who uploaded the photo
    User_ID = Column(String, nullable=False)
    
    # Name of the uploaded file
    File_Name = Column(String, nullable=False)
    
    # Name of the event related to the photo
    Event_Name = Column(String, nullable=False)
    
    # URL of the uploaded photo
    Photo_Url = Column(String, nullable=False)
    
    # Timestamp of when the photo was uploaded
    Uploaded_at = Column(DateTime, server_default=func.now(), nullable=False)

    # Relationship with the Event table
    event_photos_rel = relationship("Event", back_populates="user_register_rel")
