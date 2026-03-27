#!/usr/bin/env python3
"""
Pomodoro Timer - Focus and productivity timer
"""

import argparse
import io
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from threading import Event, Thread
import subprocess

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Configuration
SKILL_DIR = Path(__file__).parent
DATA_FILE = SKILL_DIR / "sessions.json"
CONFIG_FILE = SKILL_DIR / "config.json"
STATE_FILE = SKILL_DIR / ".state.json"

# Default settings
DEFAULT_WORK_MINUTES = 25
DEFAULT_SHORT_BREAK = 5
DEFAULT_LONG_BREAK = 15
SESSIONS_BEFORE_LONG_BREAK = 4


def load_config():
    """Load user configuration or create defaults."""
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "work_minutes": DEFAULT_WORK_MINUTES,
        "short_break_minutes": DEFAULT_SHORT_BREAK,
        "long_break_minutes": DEFAULT_LONG_BREAK,
        "sessions_before_long_break": SESSIONS_BEFORE_LONG_BREAK,
        "auto_start_breaks": False,
        "sound_enabled": True,
        "telegram_notifications": True
    }


def save_config(config):
    """Save configuration to file."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)


def load_sessions():
    """Load session history."""
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {"sessions": [], "stats": {"total_sessions": 0, "total_focus_minutes": 0}}


def save_sessions(data):
    """Save session history."""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)


def load_state():
    """Load current timer state."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return None


def save_state(state):
    """Save current timer state."""
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)


def clear_state():
    """Clear timer state."""
    if STATE_FILE.exists():
        STATE_FILE.unlink()


def get_today_sessions(sessions_data):
    """Get sessions from today."""
    today = datetime.now().strftime("%Y-%m-%d")
    return [s for s in sessions_data["sessions"] if s["date"] == today]


def get_current_session_number(sessions_data):
    """Get the current session number for today."""
    today_sessions = get_today_sessions(sessions_data)
    work_sessions = [s for s in today_sessions if s["type"] == "work"]
    return len(work_sessions)


def format_time(minutes, seconds):
    """Format time as MM:SS."""
    return f"{minutes:02d}:{seconds:02d}"


def format_duration(minutes):
    """Format duration in minutes."""
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}h {mins}m"


def notify_windows(title, message):
    """Send Windows notification."""
    try:
        # Use PowerShell for notification
        ps_cmd = f'''
        Add-Type -AssemblyName System.Windows.Forms
        $global:balloon = New-Object System.Windows.Forms.NotifyIcon
        $path = (Get-Process -id $pid).Path
        $balloon.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon($path)
        $balloon.BalloonTipIcon = [System.Windows.Forms.ToolTipIcon]::Info
        $balloon.BalloonTipText = "{message}"
        $balloon.BalloonTipTitle = "{title}"
        $balloon.Visible = $true
        $balloon.ShowBalloonTip(5000)
        '''
        subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
    except Exception:
        pass


def notify_telegram(message):
    """Send Telegram notification via OpenClaw."""
    try:
        # This will be called by the main agent
        # For now, we'll write to a notification file
        notification_file = SKILL_DIR / ".notification"
        with open(notification_file, 'w') as f:
            f.write(message)
    except Exception:
        pass


def play_sound():
    """Play a completion sound."""
    try:
        # Use Windows beep or sound
        import winsound
        winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
    except Exception:
        pass


def countdown_timer(duration_minutes, timer_type, config):
    """Run a countdown timer."""
    total_seconds = duration_minutes * 60
    end_time = datetime.now() + timedelta(minutes=duration_minutes)
    
    # Save state
    save_state({
        "type": timer_type,
        "end_time": end_time.isoformat(),
        "duration": duration_minutes,
        "started_at": datetime.now().isoformat()
    })
    
    print(f"\n🍅 {timer_type.upper()} SESSION STARTED")
    print(f"   Duration: {format_duration(duration_minutes)}")
    print(f"   Ends at: {end_time.strftime('%H:%M')}")
    print(f"\n   Press Ctrl+C to stop\n")
    
    stop_event = Event()
    
    def display_timer():
        """Display the countdown."""
        while not stop_event.is_set():
            remaining = end_time - datetime.now()
            if remaining.total_seconds() <= 0:
                break
            mins, secs = divmod(int(remaining.total_seconds()), 60)
            print(f"\r   ⏱️  {format_time(mins, secs)} remaining", end='', flush=True)
            time.sleep(1)
    
    try:
        timer_thread = Thread(target=display_timer)
        timer_thread.daemon = True
        timer_thread.start()
        
        # Wait for timer to complete or interrupt
        while datetime.now() < end_time:
            time.sleep(0.1)
            if stop_event.is_set():
                break
        
        stop_event.set()
        timer_thread.join(timeout=1)
        
        # Timer completed
        print(f"\r   ⏱️  00:00 remaining - DONE!     ")
        
        # Notifications
        if config.get("sound_enabled", True):
            play_sound()
        
        notify_windows("Pomodoro Timer", f"{timer_type.capitalize()} session complete!")
        
        return True
        
    except KeyboardInterrupt:
        stop_event.set()
        print("\n\n   ⏹️  Timer stopped by user")
        return False


def start_work_session(duration=None):
    """Start a work session."""
    config = load_config()
    sessions_data = load_sessions()
    
    if duration is None:
        duration = config.get("work_minutes", DEFAULT_WORK_MINUTES)
    
    # Check if timer already running
    state = load_state()
    if state:
        print("⚠️  A timer is already running!")
        show_status()
        return
    
    session_num = get_current_session_number(sessions_data) + 1
    print(f"\n📊 Session #{session_num} today")
    
    completed = countdown_timer(duration, "work", config)
    
    if completed:
        # Record session
        session = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "type": "work",
            "duration": duration,
            "completed": True
        }
        sessions_data["sessions"].append(session)
        sessions_data["stats"]["total_sessions"] += 1
        sessions_data["stats"]["total_focus_minutes"] += duration
        save_sessions(sessions_data)
        
        clear_state()
        
        # Suggest break
        work_sessions = get_current_session_number(sessions_data)
        if work_sessions % config.get("sessions_before_long_break", SESSIONS_BEFORE_LONG_BREAK) == 0:
            print(f"\n🎉 Great job! You've completed {work_sessions} sessions today.")
            print("   Time for a LONG break! (15 min)")
            print(f"   Run: python pomodoro.py break --long")
        else:
            print(f"\n✅ Work session complete!")
            print("   Time for a short break! (5 min)")
            print(f"   Run: python pomodoro.py break")
    else:
        clear_state()


def start_break(long_break=False):
    """Start a break session."""
    config = load_config()
    
    if long_break:
        duration = config.get("long_break_minutes", DEFAULT_LONG_BREAK)
        break_type = "long break"
    else:
        duration = config.get("short_break_minutes", DEFAULT_SHORT_BREAK)
        break_type = "break"
    
    # Check if timer already running
    state = load_state()
    if state:
        print("⚠️  A timer is already running!")
        show_status()
        return
    
    completed = countdown_timer(duration, break_type, config)
    
    if completed:
        # Record break
        sessions_data = load_sessions()
        session = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "time": datetime.now().strftime("%H:%M"),
            "type": "break" if not long_break else "long_break",
            "duration": duration,
            "completed": True
        }
        sessions_data["sessions"].append(session)
        save_sessions(sessions_data)
        
        clear_state()
        
        print(f"\n☕ Break complete! Ready to focus again?")
        print(f"   Run: python pomodoro.py start")
    else:
        clear_state()


def show_status():
    """Show current timer status."""
    state = load_state()
    
    if not state:
        print("\n⏹️  No active timer")
        
        # Show last session info
        sessions_data = load_sessions()
        today_sessions = get_today_sessions(sessions_data)
        if today_sessions:
            last = today_sessions[-1]
            print(f"\n📊 Last session: {last['type'].capitalize()} at {last['time']} ({last['duration']} min)")
            work_count = len([s for s in today_sessions if s["type"] == "work"])
            print(f"   Today's work sessions: {work_count}")
        return
    
    end_time = datetime.fromisoformat(state["end_time"])
    remaining = end_time - datetime.now()
    
    if remaining.total_seconds() <= 0:
        print(f"\n✅ {state['type'].capitalize()} session should have ended!")
        clear_state()
        return
    
    mins, secs = divmod(int(remaining.total_seconds()), 60)
    print(f"\n⏱️  {state['type'].capitalize()} session in progress")
    print(f"   Time remaining: {format_time(mins, secs)}")
    print(f"   Ends at: {end_time.strftime('%H:%M')}")


def show_stats():
    """Show productivity statistics."""
    sessions_data = load_sessions()
    today_sessions = get_today_sessions(sessions_data)
    
    print("\n📈 POMODORO STATS")
    print("=" * 40)
    
    # Today
    work_sessions = [s for s in today_sessions if s["type"] == "work"]
    total_minutes = sum(s["duration"] for s in work_sessions)
    
    print(f"\n📅 TODAY ({datetime.now().strftime('%Y-%m-%d')})")
    print(f"   Work sessions: {len(work_sessions)}")
    print(f"   Focus time: {format_duration(total_minutes)}")
    
    # This week
    week_ago = datetime.now() - timedelta(days=7)
    week_sessions = [
        s for s in sessions_data["sessions"]
        if datetime.fromisoformat(s["date"]) >= week_ago and s["type"] == "work"
    ]
    week_minutes = sum(s["duration"] for s in week_sessions)
    
    print(f"\n📊 LAST 7 DAYS")
    print(f"   Work sessions: {len(week_sessions)}")
    print(f"   Focus time: {format_duration(week_minutes)}")
    
    # All time
    print(f"\n🏆 ALL TIME")
    print(f"   Total sessions: {sessions_data['stats']['total_sessions']}")
    print(f"   Total focus time: {format_duration(sessions_data['stats']['total_focus_minutes'])}")


def list_sessions():
    """List all sessions."""
    sessions_data = load_sessions()
    sessions = sessions_data["sessions"][-20:]  # Last 20
    
    print("\n📋 RECENT SESSIONS")
    print("=" * 50)
    print(f"{'Date':<12} {'Time':<8} {'Type':<12} {'Duration':<10}")
    print("-" * 50)
    
    for s in sessions:
        print(f"{s['date']:<12} {s['time']:<8} {s['type']:<12} {s['duration']} min")


def stop_timer():
    """Stop the current timer."""
    state = load_state()
    if not state:
        print("\n⏹️  No active timer to stop")
        return
    
    print(f"\n🛑 Stopping {state['type']} session...")
    clear_state()
    print("   Timer stopped")


def main():
    parser = argparse.ArgumentParser(description="Pomodoro Timer")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Start command
    start_parser = subparsers.add_parser("start", help="Start a work session")
    start_parser.add_argument("--duration", "-d", type=int, help="Duration in minutes (default: 25)")
    
    # Break command
    break_parser = subparsers.add_parser("break", help="Start a break")
    break_parser.add_argument("--long", "-l", action="store_true", help="Long break (15 min)")
    
    # Status command
    subparsers.add_parser("status", help="Show current timer status")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop current timer")
    
    # Stats command
    subparsers.add_parser("stats", help="Show productivity statistics")
    
    # List command
    subparsers.add_parser("list", help="List recent sessions")
    
    args = parser.parse_args()
    
    if args.command == "start":
        start_work_session(args.duration)
    elif args.command == "break":
        start_break(args.long)
    elif args.command == "status":
        show_status()
    elif args.command == "stop":
        stop_timer()
    elif args.command == "stats":
        show_stats()
    elif args.command == "list":
        list_sessions()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
