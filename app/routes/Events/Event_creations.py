from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session
import os, shutil

from ...db.database import get_db
from ...schemas.Events.events_schema import validate_photofile
from ...models.Events.Events import Event
from ...models.Events.Group_photos import Group_Photos
from ...models.User.user_register import Register
from ...schemas.Events.event_participants_schema import Event_Participants_Response, Event_Members
from ...schemas.Events.events_schema import Event_Schema, EventResponse, EventUpdateRequest
from ...models.Events.Event_Participants import Event_Participants
from ...routes.User.Userlogin import get_current_user

router = APIRouter()

# ----------------------------------- Event Creation (Role: User) -----------------------------------
@router.post("/dash/create-event", response_model=EventResponse)
def create_events(
    event: Event_Schema = Depends(),
    uploaded_file: UploadFile = Depends(validate_photofile),
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    # Only users can create events
    if current_user.Role_Name == "User":
        try:
            UPLOAD_DIR = "Group_Photo"
            os.makedirs(UPLOAD_DIR, exist_ok=True)

            # Save group photo
            file_ext = uploaded_file.filename.split(".")[-1]
            unique_filename = f"{event.Event_Name}.{file_ext}"
            file_path = os.path.join(UPLOAD_DIR, unique_filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(uploaded_file.file, buffer)

            # Store photo URL in database
            new_groupphoto = Group_Photos(Photo_Url=f"/Group_Photo/{unique_filename}")
            db.add(new_groupphoto)
            db.flush()

            # Create new event
            new_event = Event(
                Event_Name=event.Event_Name,
                Description=event.Description,
                Location=event.Location,
                Date=event.Date,
                Group_Photo_ID=new_groupphoto.GID,
                Organizer_ID=current_user.UserID
            )
            db.add(new_event)
            db.commit()
            db.refresh(new_event)

            # Add organizer as a participant
            new_participant = Event_Participants(User_ID=current_user.UserID, Code=new_event.Code)
            db.add(new_participant)
            db.commit()
            db.refresh(new_participant)

            return EventResponse(
                Event_ID=new_event.Event_ID,
                Organizer_ID=new_event.Organizer_ID,
                Group_Photo_ID=new_event.Group_Photo_ID,
                Event_Name=new_event.Event_Name,
                Code=new_event.Code,
                created_at=new_event.created_at,
                updated_at=new_event.updated_at
            )

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
        finally:
            db.close()
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# ----------------------------------- Fetch All Events (Role: Admin) -----------------------------------
@router.get("/admin-dash/event/get-event", response_model=list[EventResponse])
def get_all_events(db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name != "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    events = db.query(Event).all()
    if not events:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Events Not Found")
    return events

# ----------------------------------- Fetch Event by ID (Role: Admin) -----------------------------------
@router.get("/admin-dash/event/get-event-id/{ID}", response_model=EventResponse)
def get_events_by_id(ID: str, db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name != "Admin":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
    event = db.query(Event).filter(Event.Event_ID == ID).first()
    if not event:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found")
    return event

# ----------------------------------- Fetch Events by Name (Role: Admin) -----------------------------------
@router.get("/admin-dash/event/get-event-name/{Event_Name}", response_model=list[EventResponse])
def get_events_by_Name(Event_Name: str, db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name == "Admin":
        events = db.query(Event).filter(Event.Event_Name == Event_Name).all()
        if not events:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Events Found")
        return events
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# ----------------------------------- Update Event Details (Role: User) -----------------------------------
@router.patch("/app/dash/event/update")
def update_event_details(
    update_request: EventUpdateRequest = Depends(),
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    if current_user.Role_Name == "User":
        try:
            event = db.query(Event).filter(Event.Event_Name == update_request.Event_Name).first()
            if not event:
                raise HTTPException(status_code=404, detail="Event Not Found")

            # Update fields if provided
            if update_request.New_Event_Name:
                event.Event_Name = update_request.New_Event_Name
            if update_request.Description:
                event.Description = update_request.Description
            if update_request.Location:
                event.Location = update_request.Location
            if update_request.Date:
                event.Date = update_request.Date

            db.commit()
            return {"message": "Event updated successfully"}

        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")

# ----------------------------------- Delete Event (Role: User) -----------------------------------
@router.delete("/app/dash/event/{Event_ID}")
def delete_event(Event_ID: str, db: Session = Depends(get_db), current_user: Register = Depends(get_current_user)):
    if current_user.Role_Name == "User":
        try:
            event = db.query(Event).filter(Event.Event_ID == Event_ID).first()
            if not event:
                raise HTTPException(status_code=404, detail="Event Not Found")

            # Delete associated records
            participants = db.query(Event_Participants).filter(Event_Participants.Code == event.Code).first()
            group_photo = db.query(Group_Photos).filter(Group_Photos.GID == event.Group_Photo_ID).first()
            db.delete(event)
            db.delete(group_photo)
            db.delete(participants)
            db.commit()

            return {"message": "Event Deleted Successfully"}
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized")
