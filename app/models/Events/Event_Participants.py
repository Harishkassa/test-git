from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship

from ...db.database import Base

class Event_Participants(Base):
    """
    Model representing participants who have joined events.
    """
    __tablename__ = "EventParticipants"

    # Primary Key
    Id = Column(Integer, primary_key=True)

    # Foreign Keys linking to User and Event tables
    User_ID = Column(String, ForeignKey("UserRegister.UserID", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    Code = Column(String, ForeignKey("Events.Code", ondelete="CASCADE", onupdate="CASCADE"), index=True)
    
    # Timestamp of when the user joined the event
    joined_at = Column(DateTime, server_default=func.now(), index=True, nullable=False)

    # Relationships (Code reusability portion is incomplete, needs further work)
    user_register = relationship("Register", back_populates="event_participants")
    event_rel = relationship("Event", back_populates="participants")

    # Hybrid properties to fetch related user details
    @hybrid_property
    def UserName(self):
        """Fetches the username of the participant."""
        return self.user_register.UserName if self.user_register else None
    
    @hybrid_property
    def Mobile_Number(self):
        """Fetches the mobile number of the participant."""
        return self.user_register.Mobile_Number if self.user_register else None

    @hybrid_property
    def Profile_Photo_Id(self):
        """Fetches the profile photo ID of the participant."""
        return self.user_register.Profile_Photo_Id if self.user_register else None

    @hybrid_property
    def Event_ID(self):
        """Fetches the Event ID of the participant."""
        return self.event_rel.Event_ID if self.event_rel else None