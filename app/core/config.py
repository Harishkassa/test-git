from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Database configuration
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    # Security settings
    SECURITY_KEY = os.getenv("SECURITY_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    
    # Token expiration settings
    ACESS_TOKEN_EXPERIES_MINUTES = os.getenv("ACESS_TOKEN_EXPERIES_MINUTES")
    
    # API keys
    SEND_GRID_API_KEY = os.getenv("SEND_GRID_API_KEY")

# Create an instance of Settings to access environment variables
settings = Settings()
