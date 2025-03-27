import os
import shutil
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

# Import necessary modules and dependencies
from ...db.database import get_db
from ...schemas.Events.event_photos_schema import validation_photos_files, Event_Photos_Request
from ...routes.User.Userlogin import get_current_user
from ...models.User.user_register import Register
from ...models.Events.Events_Photos import Event_Photos
from ...models.Events.Events import Event

# Initialize APIRouter
router = APIRouter()

# Upload Photos for Events (Role: User)
@router.post("/dash/event/upload-photos")
def upload_photos(
    event_request: Event_Photos_Request = Depends(),
    db: Session = Depends(get_db),
    files: List[UploadFile] = Depends(validation_photos_files),  
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name != "User":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    
    event = db.query(Event).filter(Event.Event_ID == event_request.Event_ID).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found")

    UPLOAD_DIR = "EventsPhotos"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    event_photos_list = []
    try:
        for file in files:
            file_ext = file.filename.split(".")[-1]
            unique_filename = f"{current_user.UserID}_{uuid.uuid4().hex[:8]}_{int(datetime.timestamp(datetime.now()))}.{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            event_photos_list.append(unique_filename)
            photo = Event_Photos(
                Event_ID=event.Event_ID,
                User_ID=current_user.UserID,
                File_Name=unique_filename,
                Event_Name=event.Event_Name,
                Photo_Url=f"/Ephotos/{unique_filename}"
            )
            db.add(photo)
        
        db.commit()
        return {"message": "Photos uploaded successfully", "photos": event_photos_list}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")

# Get Photos for Events (Role: User)
@router.get("/dash/event/get-photos", response_model=List[str])
def get_event_photos(
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name != "User":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    
    user_events = db.query(Event_Participants).filter(Event_Participants.User_ID == current_user.UserID).all()
    if not user_events:
        raise HTTPException(status_code=404, detail="No Events Found for this User")
    
    event_ids = [event.Event_ID for event in user_events]
    photos = db.query(Event_Photos).filter(Event_Photos.Event_ID.in_(event_ids)).all()
    if not photos:
        raise HTTPException(status_code=404, detail="No Photos Found for Your Events")
    
    return [f"/Ephotos/{photo.File_Name}" for photo in photos]

# Update Event Photos (Role: User)
@router.put("/dash/event/{Photo_Id}/upload-photos")
def update_event_photos(
    Photo_Id: str,
    file: UploadFile = Depends(validation_photos_files),
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name != "User":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    
    UPLOAD_DIR = "EventsPhotos"
    photo = db.query(Event_Photos).filter(Event_Photos.Event_Photos_ID == Photo_Id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo Not Found")

    old_photo_path = os.path.join(UPLOAD_DIR, photo.File_Name)
    if os.path.exists(old_photo_path):
        os.remove(old_photo_path)

    file_ext = file.filename.split(".")[-1]
    unique_filename = f"{current_user.UserID}.{file_ext}"
    new_photo_path = os.path.join(UPLOAD_DIR, unique_filename)

    with open(new_photo_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    photo.File_Name = unique_filename
    photo.Photo_Url = f"/Ephotos/{unique_filename}"
    db.commit()

    return {"message": "Photo updated successfully", "new_photo_url": photo.Photo_Url}

# Delete Event Photos (Role: User)
@router.delete("/dash/event/{Photo_Id}/photos")
def delete_event_photo(
    Photo_Id: str,
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name != "User":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    
    UPLOAD_DIR = "EventsPhotos"
    photo = db.query(Event_Photos).filter(Event_Photos.Event_Photos_ID == Photo_Id).first()
    if not photo:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Photo Not Found")
    
    photo_path = os.path.join(UPLOAD_DIR, photo.File_Name)
    if os.path.exists(photo_path):
        os.remove(photo_path)
    
    db.delete(photo)
    db.commit()

    return {"message": "Photo deleted successfully"}
