from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Import application settings
from ..core.config import settings

# Import Redis library
import redis

# Create database engine
engine = create_engine(settings.DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(bind=engine, autoflush=True)

# Base class for ORM models
Base = declarative_base()

# Initialize the database and create tables if they do not exist
def init_db():
    # Import all models here to ensure they are registered before creating tables
    from ..models.User.profile_photo import ProfilePhoto
    from ..models.User.user_register import Register
    from ..models.Events.Events import Event
    from ..models.Events.Group_photos import Group_Photos
    from ..models.Events.Event_Participants import Event_Participants
    from ..models.Events.Events_Photos import Event_Photos
    
    # Create tables if they do not exist
    Base.metadata.create_all(bind=engine)

# Dependency to get a new database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize Redis client for caching and background tasks
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)
