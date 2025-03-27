from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional

# Response model for event participants
class Event_Participants_Response(BaseModel):
    User_ID: str  # Unique identifier for the user
    Code: str  # Event code
    joined_at: datetime  # Timestamp of when the user joined the event

    # Configuration to allow ORM mode
    model_config = ConfigDict(from_attributes=True)

# Model for event members, extending Event_Participants_Response
class Event_Members(Event_Participants_Response):
    Event_ID : Optional[str]
    UserName: Optional[str]  # Optional username field
    Mobile_Number: Optional[str]  # Optional mobile number field
    Profile_Photo_Id: Optional[str]  # Optional profile photo identifier
