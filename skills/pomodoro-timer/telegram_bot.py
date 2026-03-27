#!/usr/bin/env python3
"""
Telegram bot integration for Pomodoro Timer
Allows controlling the timer via Telegram messages
"""

import json
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).parent
POMODORO_SCRIPT = SKILL_DIR / "pomodoro.py"
NOTIFICATION_FILE = SKILL_DIR / ".notification"


def run_command(cmd_args):
    """Run a pomodoro command and return output."""
    try:
        result = subprocess.run(
            [sys.executable, str(POMODORO_SCRIPT)] + cmd_args,
            capture_output=True,
            text=True,
            cwd=str(SKILL_DIR)
        )
        return result.stdout + result.stderr
    except Exception as e:
        return f"Error: {e}"


def handle_message(message_text):
    """Handle incoming Telegram message."""
    text = message_text.lower().strip()
    
    if text in ["/pomodoro", "/pomostart", "start pomodoro", "start work"]:
        return run_command(["start"])
    
    elif text in ["/pomobreak", "break", "start break"]:
        return run_command(["break"])
    
    elif text in ["/pomolong", "long break"]:
        return run_command(["break", "--long"])
    
    elif text in ["/pomostatus", "pomodoro status", "timer status"]:
        return run_command(["status"])
    
    elif text in ["/pomostop", "stop timer", "stop pomodoro"]:
        return run_command(["stop"])
    
    elif text in ["/pomostats", "pomodoro stats"]:
        return run_command(["stats"])
    
    elif text.startswith("/pomostart "):
        # Custom duration: /pomostart 50
        try:
            duration = int(text.split()[1])
            return run_command(["start", "--duration", str(duration)])
        except (IndexError, ValueError):
            return "Usage: /pomostart [minutes]\nExample: /pomostart 50"
    
    elif text in ["/pomohelp", "pomodoro help"]:
        return """🍅 Pomodoro Timer Commands:

/pomostart - Start 25-min work session
/pomostart 50 - Start custom duration
/pomobreak - Start 5-min break
/pomolong - Start 15-min long break
/pomostatus - Check timer status
/pomostop - Stop current timer
/pomostats - Show today's stats
/pomohelp - Show this help

Or just say: "start pomodoro", "break", "timer status", etc.
"""
    
    return None  # Not a pomodoro command


def check_notification():
    """Check if there's a notification to send."""
    if NOTIFICATION_FILE.exists():
        with open(NOTIFICATION_FILE, 'r') as f:
            message = f.read()
        NOTIFICATION_FILE.unlink()
        return message
    return None


if __name__ == "__main__":
    # Can be called directly to check notifications
    notification = check_notification()
    if notification:
        print(notification)
