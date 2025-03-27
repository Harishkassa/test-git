from pydantic import BaseModel, Field, field_validator, ConfigDict
from fastapi import File, UploadFile, HTTPException, status
from datetime import datetime, date
from typing import Optional

# Schema for event creation
class Event_Schema(BaseModel):
    Event_Name: str = Field(..., max_length=30, pattern="^[A-Za-z ]+$")  # Event name with validation
    Description: str = Field(..., min_length=10, max_length=500)  # Description length constraints
    Location: str = Field(..., min_length=2, max_length=15, pattern="^[A-Za-z ]+$")  # Location with validation
    Date: date  # Event date

# Schema for event update request
class EventUpdateRequest(BaseModel):
    Event_Name: str  # Existing event name
    New_Event_Name: Optional[str] = None  # Optional new event name
    Description: Optional[str] = None  # Optional new description
    Location: Optional[str] = None  # Optional new location
    Date: Optional[datetime] = None  # Optional new date

# File validation for event photo uploads
async def validate_photofile(uploaded_file: UploadFile = File(...)):
    ALLOWED_FILES = {"image/jpeg", "image/png"}  # Allowed file types
    MAX_SIZE = 5 * 1024 * 1024  # 5MB size limit

    # Check file type
    if uploaded_file.content_type not in ALLOWED_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only JPEG & PNG allowed."
        )
    
    # Read content to check file size
    file_content = await uploaded_file.read()
    file_size = len(file_content)

    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
    
    uploaded_file.file.seek(0)  # Reset file pointer for FastAPI processing
    return uploaded_file

# Schema for event response
class EventResponse(BaseModel):
    Event_ID: str  # Unique event identifier
    Organizer_ID: str  # ID of the event organizer
    Event_Name: str  # Name of the event
    Code: str  # Event code
    created_at: datetime  # Timestamp of event creation
    updated_at: datetime  # Timestamp of last update
    Group_Photo_ID: Optional[str]  # Optional group photo ID

    model_config = ConfigDict(from_attributes=True)  # Config to map attributes from ORM
