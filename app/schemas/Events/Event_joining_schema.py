from pydantic import BaseModel
from typing import Optional

# Schema for Event Join Request
class Event_Join_Request(BaseModel):
    Code: str  # Unique event code required to join an event
