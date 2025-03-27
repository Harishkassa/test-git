from fastapi import APIRouter, Depends, UploadFile, HTTPException, status
from sqlalchemy.orm import Session

# Importing necessary modules and dependencies
from ...db.database import get_db
from ...models.Events.Event_Participants import Event_Participants
from ...models.User.user_register import Register
from ...models.Events.Events import Event
from ...routes.User.Userlogin import get_current_user
from ...schemas.Events.event_participants_schema import Event_Participants_Response, Event_Members

# Creating APIRouter instance
router = APIRouter()

# Get Event Members of Current Event (Role: User)
@router.get("/dash/event/event-members/get-event-id/{ID}", response_model=list[Event_Members])
def get_event_by_id(
    ID: str,
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    """
    Fetch event members by event ID for users.
    """
    if current_user.Role_Name == "User":
        event = db.query(Event).filter(Event.Event_ID == ID).first()

        if not event:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found"
            )

        return db.query(Event_Participants).filter(Event_Participants.Code == event.Code).all()
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )

# Delete Event Member (Role: User)
@router.delete("/dash/event/event-member/delete-event-id/{Event_ID}/{Member_ID}", response_model=Event_Members)
def delete_event_id(
    Event_ID: str,
    Member_ID: str,
    db: Session = Depends(get_db),
    current_user: Register = Depends(get_current_user)
):
    """
    Delete a specific event member by event ID and member ID.
    """
    if current_user.Role_Name == "User":
        try:
            # Fetch the event by ID
            event = db.query(Event).filter(Event.Event_ID == Event_ID).first()
            if not event:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND, detail="Event Not Found"
                )

            # Get event members based on event code
            event_members = db.query(Event_Participants).filter(Event_Participants.Code == event.Code)

            # Fetch the specific user
            specific_user = db.query(Register).filter(Register.UserID == event_members.User_ID).first()

            # Delete the user from the database
            db.delete(specific_user)
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authorized"
        )
