from sqlalchemy.orm import relationship 
from sqlalchemy import Column, Integer, String, ForeignKey, CheckConstraint, func, DateTime, Index
from ...db.database import Base

import random, string

# Base.metadata.creat_all(bind=engine)

# generate user id
def generate_user_id():
    number_part = str(random.randint(1000,9999))
    letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))
    return "User" + number_part + letter_part 


# class model with extended Base class
class Register(Base):
    __tablename__ = "UserRegister"

    # Columns
    UserID = Column(String, primary_key=True, index=True, default = generate_user_id)
    FirstName = Column(String, nullable=False)
    LastName = Column(String, nullable=False)
    UserName = Column(String, unique=True, nullable=False)
    Gender = Column(String, index=True, nullable=False)
    Mobile_Number = Column(String, unique=True,index=True, nullable=False) 
    Email_ID = Column(String, unique=True, index=True, nullable=False)
    Password = Column(String, nullable=False)
    Role_Name = Column(String, server_default="User",index=True, nullable=False)
    create_at = Column(DateTime, server_default=func.now(), nullable=False)
    update_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    Profile_Photo_Id = Column(String, ForeignKey("profile_photo.Photo_ID",ondelete="CASCADE", onupdate="CASCADE"),index=True)

    # Constraints for Data Validation
    __tableargs__ = (
        CheckConstraint('"FirstName" ~ \'^[A-Za-z]+$\'', name="Valid_FirstName"),
        CheckConstraint('"LastName" ~ \'^[A-Za-z]+$\'', name="Valid_LastName"),
        CheckConstraint('"UserName" ~ \'^[a-zA-Z0-9_]+$\'' , name="Valid_UserName"),
        CheckConstraint('"Mobile_Number" ~ \'^[0-9]{10}$\'', name="Valid_Mobile_Number"),
        CheckConstraint('"Email_ID" ~ \'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$\'', name="Valid_EmailId"),
        CheckConstraint('"Password" ~ \'^(?=.*[a-z])(?=.*[A-Z])(?=.*\\d)(?=.*[@$!%*?&])[A-Za-z\\d@$!%*?&]{8,}$\'', name="Valid_Password"),
    )

    # relationship with profilephoto (one to one)
    profile_photo = relationship("ProfilePhoto", back_populates="user_register", uselist=False) # One-to-One Relationship with ProfilePhoto
    Events = relationship("Event", back_populates="user_register")  # One-to-Many Relationship with Events
    event_participants = relationship("Event_Participants", back_populates="user_register")  # Many-to-Many Relationship with Event Participants
