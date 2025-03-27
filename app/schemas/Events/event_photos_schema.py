from pydantic import BaseModel, Field, ConfigDict
from typing import List
from fastapi import UploadFile, File, HTTPException, status
from datetime import datetime

# Request model for uploading event photos
class Event_Photos_Request(BaseModel):
    Event_ID: str

# Function to validate uploaded photo files
async def validation_photos_files(uploaded_photo_file: List[UploadFile] = File(...)):
    validated_files = []

    # Allowed file types and maximum file size (5MB)
    ALLOWED_FILES = {"jpeg", "png"}
    MAX_SIZE = 5 * 1024 * 1024  # 5MB

    for file in uploaded_photo_file:
        file_ext = file.filename.split(".")[-1].lower()
        
        # Check if file format is allowed
        if file_ext not in ALLOWED_FILES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=f"Invalid file format: {file.filename}. Allowed types: JPEG, PNG"
            )
        
        # Read file content to check size
        file_content = await file.read()  
        file_size = len(file_content)

        # Check if file size exceeds limit
        if file_size > MAX_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File too large: {file.filename} (Max: 5MB)."
            )

        file.file.seek(0)  # Reset file pointer for next processing
        validated_files.append(file) 

    return validated_files  
    
# Response model for event photos
class Event_Photos_Response(BaseModel):
    Event_Photos_ID: str
    Event_ID: str
    User_ID: str
    Event_Name: str
    Photo_Url: str
    Uploaded_at: datetime
    
    # Configuration for model serialization
    model_config = ConfigDict(from_attributes=True)
