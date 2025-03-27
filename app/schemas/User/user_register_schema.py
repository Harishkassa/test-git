from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from fastapi import File, UploadFile, HTTPException, status
from typing import Literal, Optional
import re

# User Registration Schema
class UserRegisterJson(BaseModel):
    FirstName: str = Field(..., min_length=2, max_length=20, pattern="^[A-Za-z]+$")  # Only letters allowed
    LastName: str = Field(..., min_length=2, max_length=20, pattern="^[A-Za-z]+$")  # Only letters allowed
    UserName: str = Field(..., min_length=2, max_length=20, pattern=r"^[a-zA-Z0-9_]+$")  # Alphanumeric and underscore allowed
    Gender: Literal["Male", "Female", "Other"]  # Restricting to specific choices
    Mobile_Number: str = Field(..., pattern=r"^\d{10}$")  # Must be a 10-digit number
    Email_ID: EmailStr  # Valid email format enforced
    Password: str = Field(..., min_length=8, max_length=50)  # Password length constraints

    # Password validation
    @field_validator("Password")
    @classmethod
    def validate_password(cls, value):
        if not re.search(r"[a-z]", value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one lowercase letter.")
        if not re.search(r"[A-Z]", value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one capital letter.")
        if not re.search(r"\d", value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one digit.")
        if not re.search(r"[@$!%*?&]", value):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password must contain at least one special character (@$!%*?&).")
        return value

# User Update Schema
class UserUpdateRequest(BaseModel):
    FirstName: Optional[str] = None  # Optional field for updating first name
    LastName: Optional[str] = None  # Optional field for updating last name
    UserName: str  # Existing username required
    New_UserName: Optional[str] = None  # Optional field for changing username
    Gender: Optional[str] = None  # Optional gender update
    Mobile_Number: Optional[str] = None  # Optional mobile number update
    Email_ID: Optional[EmailStr] = None  # Optional email update

# File Validation Function
async def validate_file(uploaded_file: UploadFile = File(...)):
    ALLOWED_FILES = {"image/jpeg", "image/png"}  # Allowed file types
    MAX_SIZE = 5 * 1024 * 1024  # Max file size (5MB)

    # Check file type
    if uploaded_file.content_type not in ALLOWED_FILES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Invalid file type. Only JPEG & PNG allowed."
        )

    # Read file content to check size
    file_content = await uploaded_file.read()
    file_size = len(file_content)

    if file_size > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")

    uploaded_file.file.seek(0)  # Reset file pointer for FastAPI processing
    return uploaded_file

# User Response Schema
class UserResponse(BaseModel):
    User_ID: str  # Unique user identifier
    FirstName: str  # User's first name
    LastName: str  # User's last name
    UserName: str  # User's chosen username
    Gender: str  # User's gender
    Mobile_Number: str  # User's mobile number
    Email_ID: EmailStr  # User's email address
    Role_Name: str = "User"  # Default role for users
    Profile_Photo_Id: Optional[str]  # Optional profile photo identifier

    model_config = ConfigDict(from_attributes=True)  # FastAPI 0.95+ compatibility
