from pydantic import BaseModel, Field
from datetime import datetime

# Pydantic model for profile photo response
class Profile_Photo_Response(BaseModel):
    Photo_ID: str  # Unique identifier for the photo
    Photo_Url: str  # URL where the photo is stored
    Photo_Type: str  # Type of photo (e.g., JPEG, PNG)
    uploaded_at: str  # Timestamp when the photo was uploaded
    
    # Config to allow ORM model conversion
    model_config = ConfigDict(from_attributes=True)
