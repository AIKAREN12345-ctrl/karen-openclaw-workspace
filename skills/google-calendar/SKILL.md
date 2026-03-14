---
name: google_calendar
description: Google Calendar integration for proactive intelligence
metadata:
  openclaw:
    requires:
      tools: ["web_fetch", "browser"]
    tags: ["calendar", "google", "gmail", "schedule", "proactive"]
    author: "Karen"
    version: "1.0.0"
---

# Google Calendar Integration

Access your Google Calendar to provide proactive assistance based on your schedule.

## Setup Instructions

### 1. Enable Google Calendar API

1. Go to https://console.cloud.google.com/
2. Create a new project (or use existing)
3. Enable the **Google Calendar API**
4. Create OAuth 2.0 credentials (Desktop app)
5. Download the client credentials JSON

### 2. Authenticate

Run the authentication flow:
```bash
/skill google_calendar auth
```

This will:
- Open a browser to Google OAuth
- Request Calendar read-only access
- Store the refresh token securely

### 3. Permissions Requested

**ONLY Calendar access:**
- ✅ View your calendars
- ✅ View events on your calendars
- ✅ Add events to your calendars (optional, for reminders)

**NO Gmail access:**
- ❌ Cannot read emails
- ❌ Cannot send emails
- ❌ Cannot access contacts

## Usage

### Check Today's Schedule
```
/skill google_calendar today
```

### Check Upcoming Events
```
/skill google_calendar upcoming --hours 24
```

### Add Proactive Reminder
```
/skill google_calendar remind "Meeting with team" --before 30min
```

## Proactive Intelligence

Once connected, I can:

- **Morning brief:** "You have 3 meetings today, first at 9 AM"
- **Travel alerts:** "Meeting in city center at 2 PM - traffic is heavy"
- **Prep reminders:** "Doctor appointment tomorrow - want me to prepare questions?"
- **Follow-ups:** "You met with X last week - want to schedule follow-up?"
- **Conflict detection:** "New meeting conflicts with your lunch block"

## Privacy & Security

- Token stored locally in `~/.openclaw/secrets/`
- Can revoke access anytime at https://myaccount.google.com/permissions
- Read-only by default (can add events if you enable)
- No email access, ever

## Automation

Add to cron for daily morning brief:
```json5
{
  name: "morning-calendar-brief",
  schedule: "0 8 * * *",
  command: "/skill google_calendar today --notify"
}
```
