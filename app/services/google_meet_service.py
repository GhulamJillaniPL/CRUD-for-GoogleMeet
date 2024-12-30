# File: app/services/google_meet_service.py
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime, timedelta
import pickle
import os.path
from typing import List, Optional
from ..models import Meeting, MeetingCreate, MeetingUpdate
from fastapi.encoders import jsonable_encoder
from ..config import settings

SCOPES = ['https://www.googleapis.com/auth/calendar']

class GoogleMeetService:
    def __init__(self):
        self.creds = self._get_credentials()
        self.service = build('calendar', 'v3', credentials=self.creds)

    def _get_credentials(self):
        creds = None
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
                
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    settings.google_credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)

        return creds

    def create_meeting(self, meeting: MeetingCreate) -> Meeting:
        try:
            # Calculate end time
            end_time = meeting.start_time + timedelta(minutes=meeting.duration)

            # Create event with Google Meet conference
            event = {
                'summary': meeting.title,
                'description': meeting.description,
                'start': {
                    'dateTime': meeting.start_time.isoformat(),
                    'timeZone': meeting.timezone,
                },
                'end': {
                    'dateTime': end_time.isoformat(),
                    'timeZone': meeting.timezone,
                },
                'conferenceData': {
                    'createRequest': {
                        'requestId': f"{meeting.title}-{datetime.now().timestamp()}",
                        'conferenceSolutionKey': {'type': 'hangoutsMeet'}
                    }
                },
                'attendees': [{'email': attendee} for attendee in meeting.attendees]
            }

            # Create the event with conferenceDataVersion=1 to enable Meet
            event = self.service.events().insert(
                calendarId='primary',
                body=event,
                conferenceDataVersion=1
            ).execute()

            # Extract the Meet link
            meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')

            return Meeting(
                id=event['id'],
                title=event['summary'],
                description=event.get('description', ''),
                start_time=datetime.fromisoformat(event['start']['dateTime']),
                duration=meeting.duration,
                timezone=event['start']['timeZone'],
                meet_link=meet_link,
                attendees=[attendee['email'] for attendee in event.get('attendees', [])]
            )
        except Exception as e:
            raise Exception(f"Failed to create meeting: {str(e)}")

    def get_meeting(self, meeting_id: str) -> Meeting:
        try:
            event = self.service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()

            start_time = datetime.fromisoformat(event['start']['dateTime'])
            end_time = datetime.fromisoformat(event['end']['dateTime'])
            duration = int((end_time - start_time).total_seconds() / 60)
            
            meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')

            return Meeting(
                id=event['id'],
                title=event['summary'],
                description=event.get('description', ''),
                start_time=start_time,
                duration=duration,
                timezone=event['start']['timeZone'],
                meet_link=meet_link,
                attendees=[attendee['email'] for attendee in event.get('attendees', [])]
            )
        except Exception as e:
            raise Exception(f"Failed to get meeting: {str(e)}")

    def list_meetings(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Meeting]:
        try:
            if not start_date:
                start_date = datetime.now()
            if not end_date:
                end_date = start_date + timedelta(days=7)

            # Removed conferenceDataVersion parameter
            events_result = self.service.events().list(
                calendarId='primary',
                timeMin=start_date.isoformat() + 'Z',
                timeMax=end_date.isoformat() + 'Z',
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            meetings = []
            for event in events_result.get('items', []):
                # Check if event has conference data (Google Meet)
                if 'conferenceData' in event and 'start' in event and 'dateTime' in event['start']:
                    start_time = datetime.fromisoformat(event['start']['dateTime'].replace('Z', ''))
                    end_time = datetime.fromisoformat(event['end']['dateTime'].replace('Z', ''))
                    duration = int((end_time - start_time).total_seconds() / 60)
                    
                    # Safely get the meet link
                    meet_link = ''
                    entry_points = event.get('conferenceData', {}).get('entryPoints', [])
                    for entry in entry_points:
                        if entry.get('entryPointType') == 'video':
                            meet_link = entry.get('uri', '')
                            break

                    meetings.append(Meeting(
                        id=event['id'],
                        title=event['summary'],
                        description=event.get('description', ''),
                        start_time=start_time,
                        duration=duration,
                        timezone=event['start'].get('timeZone', 'UTC'),
                        meet_link=meet_link,
                        attendees=[
                            attendee['email'] 
                            for attendee in event.get('attendees', [])
                        ]
                    ))

            return meetings
        except Exception as e:
            raise Exception(f"Failed to list meetings: {str(e)}")

    def update_meeting(self, meeting_id: str, meeting: MeetingUpdate) -> Meeting:
        try:
            # Get existing event
            event = self.service.events().get(
                calendarId='primary',
                eventId=meeting_id
            ).execute()

            # Update only provided fields
            if meeting.title is not None:
                event['summary'] = meeting.title
            if meeting.description is not None:
                event['description'] = meeting.description
            if meeting.start_time is not None:
                event['start']['dateTime'] = meeting.start_time.isoformat()
                end_time = meeting.start_time + timedelta(minutes=meeting.duration or 60)
                event['end']['dateTime'] = end_time.isoformat()
            if meeting.timezone is not None:
                event['start']['timeZone'] = meeting.timezone
                event['end']['timeZone'] = meeting.timezone
            if meeting.attendees is not None:
                event['attendees'] = [{'email': email} for email in meeting.attendees]

            updated_event = self.service.events().update(
                calendarId='primary',
                eventId=meeting_id,
                body=event,
                conferenceDataVersion=1
            ).execute()

            start_time = datetime.fromisoformat(updated_event['start']['dateTime'])
            end_time = datetime.fromisoformat(updated_event['end']['dateTime'])
            duration = int((end_time - start_time).total_seconds() / 60)
            meet_link = updated_event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')

            return Meeting(
                id=updated_event['id'],
                title=updated_event['summary'],
                description=updated_event.get('description', ''),
                start_time=start_time,
                duration=duration,
                timezone=updated_event['start']['timeZone'],
                meet_link=meet_link,
                attendees=[attendee['email'] for attendee in updated_event.get('attendees', [])]
            )
        except Exception as e:
            raise Exception(f"Failed to update meeting: {str(e)}")

    def delete_meeting(self, meeting_id: str):
        try:
            self.service.events().delete(
                calendarId='primary',
                eventId=meeting_id
            ).execute()
        except Exception as e:
            raise Exception(f"Failed to delete meeting: {str(e)}")