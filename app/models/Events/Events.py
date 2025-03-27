from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func, Date
from sqlalchemy.orm import relationship
import random, string

from ...db.database import Base

# Function to generate a unique Event ID
def generate_event_id():
    number_part = str(random.randint(1000, 9999))
    letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))
    return "EID" + number_part + letter_part

# Function to generate a unique Event Code
def generate_event_code():
    parts = ["".join(random.choices(string.ascii_uppercase, k=3)) for _ in range(3)]
    return "-".join(parts)

class Event(Base):
    __tablename__ = "Events"

    # Primary Key: Unique Event ID
    Event_ID = Column(String, primary_key=True, index=True, default=generate_event_id)
    
    # Event details
    Event_Name = Column(String, index=True, nullable=False)
    Description = Column(String, nullable=False)
    Location = Column(String, index=True, nullable=False)
    Date = Column(Date, index=True, nullable=False)
    Code = Column(String, unique=True, nullable=False, default=generate_event_code)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Statistics
    Total_Photos = Column(Integer, default=0, index=True, nullable=False)
    Total_Members = Column(Integer, default=1, index=True, nullable=False)
    
    # Foreign Keys
    Group_Photo_ID = Column(String, ForeignKey("Group_Photos_Table.GID", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    Organizer_ID = Column(String, ForeignKey("UserRegister.UserID", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    
    # Relationships
    user_register = relationship("Register", back_populates="Events")
    group_photos = relationship("Group_Photos", back_populates="events", uselist=False)
    participants = relationship("Event_Participants", back_populates="event_rel")
    user_register_rel = relationship("Event_Photos", back_populates="event_photos_rel")
