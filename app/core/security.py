from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

# Import application settings
from .config import settings

# Password hashing context setup
pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

class hash:
    """
    A utility class for password hashing and verification.
    """
    
    @staticmethod
    def hashing(Password: str):
        """Hashes a given password using bcrypt."""
        return pwd_cxt.hash(Password)

    @staticmethod
    def verify(plain_password: str, hashed_password: str):
        """Verifies a plain password against its hashed version."""
        return pwd_cxt.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    """
    Generates a JWT access token with an expiration time.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACESS_TOKEN_EXPERIES_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECURITY_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_access(token: str):
    """
    Verifies and decodes a JWT access token.
    Returns the payload if valid, otherwise returns None.
    """
    try:
        payload = jwt.decode(token, settings.SECURITY_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
