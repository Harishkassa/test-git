from fastapi import HTTPException, APIRouter, Depends
from celery import Celery
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Importing project-specific modules
from ..core.config import settings
from ..db.database import Base, get_db, redis_client

import ssl
import redis

# Initialize Celery application
celery_app = Celery(
    "tasks",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

@celery_app.task
def send_email_task(email, otp):
    """
    Celery task to send an OTP email using SendGrid.
    """
    message = Mail(
        from_email="haristudent4@gmail.com",
        to_emails=email,
        subject="Your OTP Code",
        plain_text_content=f"Your OTP Code is: {otp}"
    )   
    try:
        sg = SendGridAPIClient(settings.SEND_GRID_API_KEY)
        
        # Quick Fix: Bypass SSL verification (Not recommended for production)
        ssl._create_default_https_context = ssl._create_unverified_context
        
        sg.send(message)
        return "OTP Sent Successfully"
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
