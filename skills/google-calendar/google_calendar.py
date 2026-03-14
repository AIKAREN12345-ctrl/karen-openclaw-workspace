#!/usr/bin/env python3
"""
Google Calendar Integration
Handles OAuth and calendar API calls
"""

import os
import json
import pickle
from datetime import datetime, timedelta
from pathlib import Path

# Google API imports (will be installed)
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
except ImportError:
    print("Google API libraries not installed. Run: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
    exit(1)

# If modifying these scopes, delete the token file
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class GoogleCalendarSkill:
    def __init__(self):
        self.workspace = Path.home() / ".openclaw" / "workspace"
        self.secrets_dir = Path.home() / ".openclaw" / "secrets"
        self.secrets_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.secrets_dir / "google-calendar-token.pickle"
        self.creds_file = self.secrets_dir / "google-calendar-credentials.json"
    
    def authenticate(self):
        """Run OAuth flow to get credentials"""
        creds = None
        
        # Load existing token
        if self.token_file.exists():
            with open(self.token_file, 'rb') as token:
                creds = pickle.load(token)
        
        # If no valid credentials, run auth flow
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not self.creds_file.exists():
                    print(f"ERROR: Credentials file not found at {self.creds_file}")
                    print("Please download OAuth credentials from Google Cloud Console")
                    return None
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.creds_file), SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for future runs
            with open(self.token_file, 'wb') as token:
                pickle.dump(creds, token)
        
        return creds
    
    def get_today_events(self):
        """Get today's calendar events"""
        creds = self.authenticate()
        if not creds:
            return []
        
        try:
            service = build('calendar', 'v3', credentials=creds)
            
            # Get today's date range
            now = datetime.utcnow()
            start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = start_of_day + timedelta(days=1)
            
            # Format for API
            time_min = start_of_day.isoformat() + 'Z'
            time_max = end_of_day.isoformat() + 'Z'
            
            # Call Calendar API
            events_result = service.events().list(
                calendarId='primary',
                timeMin=time_min,
                timeMax=time_max,
                maxResults=10,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = events_result.get('items', [])
            return events
            
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []
    
    def format_events(self, events):
        """Format events for display"""
        if not events:
            return "No events scheduled for today."
        
        output = f"📅 Today's Schedule ({len(events)} events):\n\n"
        
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            summary = event.get('summary', 'No title')
            location = event.get('location', '')
            
            # Format time
            if 'T' in start:  # dateTime format
                dt = datetime.fromisoformat(start.replace('Z', '+00:00'))
                time_str = dt.strftime('%I:%M %p')
            else:  # All-day event
                time_str = 'All day'
            
            output += f"• {time_str} - {summary}"
            if location:
                output += f" (📍 {location})"
            output += "\n"
        
        return output

def main():
    """Main entry point"""
    import sys
    
    skill = GoogleCalendarSkill()
    
    if len(sys.argv) < 2:
        print("Usage: google_calendar.py [auth|today|upcoming]")
        return
    
    command = sys.argv[1]
    
    if command == "auth":
        print("Starting Google Calendar authentication...")
        creds = skill.authenticate()
        if creds:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed")
    
    elif command == "today":
        events = skill.get_today_events()
        print(skill.format_events(events))
    
    elif command == "upcoming":
        # TODO: Implement upcoming events
        print("Upcoming events feature not yet implemented")
    
    else:
        print(f"Unknown command: {command}")
        print("Usage: google_calendar.py [auth|today|upcoming]")

if __name__ == "__main__":
    main()
