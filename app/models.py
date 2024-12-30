from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
import json

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

class MeetingBase(BaseModel):
    title: str
    description: Optional[str] = ""
    start_time: datetime
    duration: int = 60  # Duration in minutes
    timezone: str = "UTC"
    attendees: List[str] = []

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        arbitrary_types_allowed = True

class MeetingCreate(MeetingBase):
    pass

class MeetingUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    duration: Optional[int] = None
    timezone: Optional[str] = None
    attendees: Optional[List[str]] = None

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        arbitrary_types_allowed = True

class Meeting(MeetingBase):
    id: str
    meet_link: str

    class Config:
        json_encoders = {
            datetime: lambda dt: dt.isoformat()
        }
        orm_mode = True
        arbitrary_types_allowed = True