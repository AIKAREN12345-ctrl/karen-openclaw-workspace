# Pomodoro Timer Skill

A productivity timer for focused work sessions with break reminders.

## Usage

```bash
# Start a work session (25 min default)
python skills/pomodoro-timer/pomodoro.py start

# Start with custom duration (minutes)
python skills/pomodoro-timer/pomodoro.py start --duration 50

# Start a break (5 min default)
python skills/pomodoro-timer/pomodoro.py break

# Start long break (15 min)
python skills/pomodoro-timer/pomodoro.py break --long

# Check current timer status
python skills/pomodoro-timer/pomodoro.py status

# Stop current timer
python skills/pomodoro-timer/pomodoro.py stop

# View today's stats
python skills/pomodoro-timer/pomodoro.py stats

# List all sessions
python skills/pomodoro-timer/pomodoro.py list
```

## Features

- **Work sessions**: 25 min default (configurable)
- **Short breaks**: 5 min default
- **Long breaks**: 15 min after 4 work sessions
- **Session tracking**: Logs all completed sessions
- **Stats**: Daily/weekly productivity reports
- **Notifications**: Desktop + Telegram when timer completes
- **Auto-break suggestion**: Prompts for break after work session

## Files

- `pomodoro.py` - Main timer script
- `sessions.json` - Session history
- `config.json` - User preferences

## Integration

Can be triggered via:
- Cron jobs for scheduled focus time
- Telegram bot commands
- Manual CLI usage
