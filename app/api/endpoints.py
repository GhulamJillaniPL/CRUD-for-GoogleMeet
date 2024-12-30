from fastapi import APIRouter, HTTPException
from ..services.google_meet_service import GoogleMeetService
from ..models import Meeting, MeetingCreate, MeetingUpdate
from datetime import datetime
from typing import Optional, List
from fastapi.encoders import jsonable_encoder

router = APIRouter()
google_meet_service = GoogleMeetService()

@router.post("/meetings", response_model=Meeting)
async def create_meeting(meeting: MeetingCreate):
    """Create a new Google Meet meeting"""
    try:
        # Convert to dict and handle datetime serialization
        meeting_data = jsonable_encoder(meeting)
        return google_meet_service.create_meeting(meeting)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/meetings/{meeting_id}", response_model=Meeting)
async def get_meeting(meeting_id: str):
    """Get details of a specific meeting"""
    try:
        return google_meet_service.get_meeting(meeting_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/meetings", response_model=List[Meeting])
async def list_meetings(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """List all meetings within a date range"""
    try:
        return google_meet_service.list_meetings(start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/meetings/{meeting_id}", response_model=Meeting)
async def update_meeting(meeting_id: str, meeting: MeetingUpdate):
    """Update an existing meeting"""
    try:
        # Convert to dict and handle datetime serialization
        meeting_data = jsonable_encoder(meeting)
        return google_meet_service.update_meeting(meeting_id, meeting)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """Delete a meeting"""
    try:
        google_meet_service.delete_meeting(meeting_id)
        return {"message": f"Meeting {meeting_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))