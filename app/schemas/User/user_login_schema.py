from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Model for user login request
class LoginRequest(BaseModel):
    identifier: str = Field(..., description="User identifier (username or email)")
    Password: str = Field(..., description="User password")

# Model for login response containing user details and authentication token
class LoginResponse(BaseModel):
    UserName: str  # Username of the logged-in user
    Role_Name: str  # Role assigned to the user
    access_token: str  # JWT access token
    token_type: str  # Type of token (e.g., "Bearer")

# Model for OTP verification request
class otp_verification(BaseModel):
    Email_ID: EmailStr  # Email ID where OTP was sent
    otp: str  # OTP code for verification

# Model for storing token-related data
class TokenData(BaseModel):
    Password: Optional[str] = None  # Optional password field
    Role_Name: Optional[str] = None  # Optional role field
