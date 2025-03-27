# from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, func
# from sqlalchemy.orm import relationship

# from ..db.database import Base

# def generate_id():
#     number_part = str(random.randint(1000,9999))
#     letter_part = ''.join(random.choices(string.ascii_uppercase, k=3))
#     return "Notifiy" + number_part + letter_part

# class Notification(Base):
#     __tablename__ = "Notificatons"

#     ID = Column(String, primary_key=True, index=True, default=generate_id)
#     Event_ID = Column(String, ForeignKey("Events.Event_ID",ondelete="CASCADE"),index=True)
#     User_ID = Column(String, ForeignKey("UserRegister.UserID", ondelete="CASCADE"),index=True)
#     Message = Column(String, nullable=False)
#     created_at = Column(DateTime,server_default=func.now(), nullable=False)