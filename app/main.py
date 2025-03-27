from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# Importing route modules
from .routes.User import Userregister, Userlogin
from .routes.Events import (
    Event_creations, 
    Event_Participants_routes, 
    Event_joining_routes, 
    Event_Photos_routes
)

# Initialize FastAPI app
app = FastAPI(title="Fllama")

# Mount the "EventsPhotos" directory to serve images
app.mount("/Ephotos", StaticFiles(directory="EventsPhotos"), name="photos")

# Initialize the database
from .db.database import init_db
init_db()

# Registering routers for different functionalities
app.include_router(Userregister.router, prefix="/app", tags=["Register"])
app.include_router(Userlogin.router, tags=["Login"])
app.include_router(Event_creations.router, prefix="/app", tags=["Event"])
app.include_router(Event_Participants_routes.router, prefix="/app", tags=["Event Members"])
app.include_router(Event_joining_routes.router, prefix="/app", tags=["Join Event"])
app.include_router(Event_Photos_routes.router, prefix="/app", tags=["Event Photos"])
