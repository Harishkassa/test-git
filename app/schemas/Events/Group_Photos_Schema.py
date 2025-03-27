from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional

# Response model for group photos
class Group_Photos_Response(BaseModel):
    GID: str  # Group ID
    Photo_Url: str  # URL of the uploaded photo
    Uploaded_at: datetime  # Timestamp of when the photo was uploaded

    # Enable Orm support , Configdict : dict like configuration object
    model_config = ConfigDict(from_attributes=True)
