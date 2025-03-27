# from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
# from sqlalchemy.orm import relationship

# from ..db.database import Base

# import random, string

# def generate_id():
#     number_part = str(random.randint(1000,9999))
#     letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))
#     return "ID" + number_part + letter_part

# class LogActivity(Base):
#     __tablename__ = "Log_Activity"

#     ID = Column(String, primary_key=True, index=True, default=generate_id)
#     UserID = Column(String, ForeignKey("UserRegister.UserID",ondelete="CASCADE"),index=True)
#     Message = Column(String, index=True, nullable=False)
#     created_at = Column(DateTime, server_default=func.now(),nullable=False)

#     user_register = relationship("UserRegister", back_populates="log_activity")