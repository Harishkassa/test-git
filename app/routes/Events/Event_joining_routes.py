from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

# Import necessary modules
from ...db.database import get_db
from ...schemas.Events.events_schema import validate_photofile
from ...models.Events.Event_Participants import Event_Participants
from ...models.Events.Events import Event
from ...models.Events.Group_photos import Group_Photos
from ...models.User.user_register import Register
from ...schemas.Events.Event_joining_schema import Event_Join_Request
from ...schemas.Events.events_schema import EventResponse
from ...schemas.Events.event_participants_schema import Event_Participants_Response, Event_Members
from ...routes.User.Userlogin import get_current_user
from ...routes.Events.Event_creations import create_events

# Initialize API Router
router = APIRouter()

# Endpoint to Join Events (Role: User)
@router.post("/dash/join-event/{code}")
def join_events(
    code: Event_Join_Request = Depends(),
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user),
):
    # Ensure only users can join events
    if current_user.Role_Name == "User":
        try:
            # Check if event exists
            event = db.query(Event).filter(Event.Code == code.Code).first()
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Code is Invalid Or Not Found",
                )
            
            # Check if user is already enrolled in the event
            existing_user = db.query(Event_Participants).filter(
                Event_Participants.User_ID == current_user.UserID,
                Event_Participants.Code == code.Code,
            ).first()
            if existing_user:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You are already Enrolled in that...",
                )
            
            # Add user to event participants
            event_join = Event_Participants(
                User_ID=current_user.UserID,
                Code=code.Code,
                Profile_Photo_Id=current_user.Profile_Photo_Id,
            )
            db.add(event_join)
            db.commit()
            return "Successfully Added In Event"
        
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error: {str(e)}",
            )
    
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )

# Endpoint to View All Joined Events (Role: User)
@router.get("/dash/event", response_model=list[Event_Members])
def view_joined_events(
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user),
):
    # Ensure only users can view joined events
    if current_user.Role_Name != "User":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not Authorized",
        )
    
    # Check if user has joined any events
    joined_events = db.query(Event_Participants).filter(
        Event_Participants.User_ID == current_user.UserID
    ).first()
    
    if not joined_events:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not Joined in any events Yet",
        )
    
    # Return all joined events
    return db.query(Event_Participants).filter(
        Event_Participants.User_ID == current_user.UserID
    ).all()
