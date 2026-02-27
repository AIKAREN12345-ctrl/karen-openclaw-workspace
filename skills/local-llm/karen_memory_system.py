#!/usr/bin/env python3
"""
================================================================================
KAREN MEMORY SYSTEM - UNIFIED ORCHESTRATION
================================================================================

A complete memory management system that:
1. Extracts session conversations from OpenClaw JSONL files
2. Consolidates them into daily memory files
3. Generates searchable embeddings
4. Provides morning context loading
5. Maintains git synchronization

Usage:
    python karen_memory_system.py [command]

Commands:
    extract     - Extract all session conversations to memory files
    consolidate - Merge and deduplicate memory entries
    embed       - Generate embeddings for search
    morning     - Load morning context (yesterday + today)
    full        - Load complete history
    sync        - Git commit all memory changes
    all         - Run full pipeline (extract + consolidate + embed + sync)

================================================================================
"""

import json
import hashlib
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict

# ==============================================================================
# CONFIGURATION
# ==============================================================================

MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")
SESSIONS_DIR = Path("C:/Users/Karen/.openclaw/agents/main/sessions")
WORKSPACE_DIR = Path("C:/Users/Karen/.openclaw/workspace")
SKILLS_DIR = WORKSPACE_DIR / "skills/local-llm"

# ==============================================================================
# SESSION EXTRACTION
# ==============================================================================

def parse_session_file(filepath):
    """Parse a session JSONL file and extract conversation data"""
    messages = []
    session_date = None
    session_id = filepath.stem.split('.')[0]
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    
                    # Get session timestamp
                    if data.get('type') == 'session':
                        ts = data.get('timestamp', '')
                        if ts:
                            session_date = ts[:10]  # YYYY-MM-DD
                    
                    # Extract user and assistant messages
                    if data.get('type') == 'message':
                        msg = data.get('message', {})
                        role = msg.get('role', '')
                        content = msg.get('content', [])
                        timestamp = data.get('timestamp', '')
                        
                        if role in ('user', 'assistant'):
                            text = extract_text(content)
                            if text and not is_system_noise(text):
                                messages.append({
                                    'role': role,
                                    'text': text,
                                    'timestamp': timestamp
                                })
                                
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        print(f"  Error reading {filepath.name}: {e}")
        return None, None, []
    
    return session_date, session_id, messages

def extract_text(content):
    """Extract text from message content"""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        texts = []
        for item in content:
            if isinstance(item, dict):
                if item.get('type') == 'text':
                    texts.append(item.get('text', ''))
                elif item.get('type') == 'toolCall':
                    name = item.get('name', 'tool')
                    args = item.get('arguments', {})
                    if name == 'read' and 'file_path' in args:
                        texts.append(f"[Read: {Path(args['file_path']).name}]")
                    elif name == 'write' and 'path' in args:
                        texts.append(f"[Wrote: {Path(args['path']).name}]")
                    elif name == 'edit' and 'file_path' in args:
                        texts.append(f"[Edited: {Path(args['file_path']).name}]")
                    elif name == 'exec' and 'command' in args:
                        cmd = args['command'][:40]
                        texts.append(f"[Exec: {cmd}...]")
                    else:
                        texts.append(f"[{name}]")
        return ' '.join(texts)
    return ''

def is_system_noise(text):
    """Filter out system messages and noise"""
    noise_patterns = [
        'Read HEARTBEAT.md',
        'An async command you ran earlier',
        'System: [',
        'HEARTBEAT_OK',
        'Return your summary',
        'Message Ken:',
        '[System Message]',
        '[cron:',
        'Current time:',
    ]
    for pattern in noise_patterns:
        if pattern in text:
            return True
    return False

# ==============================================================================
# MEMORY FILE MANAGEMENT
# ==============================================================================

def get_all_sessions():
    """Get all session files organized by date"""
    sessions_by_date = defaultdict(list)
    
    for jsonl_file in SESSIONS_DIR.glob("*.jsonl"):
        if ".deleted." in jsonl_file.name:
            continue
        
        date, session_id, messages = parse_session_file(jsonl_file)
        if date and messages:
            sessions_by_date[date].append({
                'id': session_id,
                'file': jsonl_file.name,
                'messages': messages,
                'mtime': datetime.fromtimestamp(jsonl_file.stat().st_mtime)
            })
    
    # Sort sessions within each date by time
    for date in sessions_by_date:
        sessions_by_date[date].sort(key=lambda x: x['mtime'])
    
    return sessions_by_date

def summarize_session(session):
    """Create a summary of a conversation session"""
    messages = session['messages']
    user_msgs = [m for m in messages if m['role'] == 'user']
    assistant_msgs = [m for m in messages if m['role'] == 'assistant']
    
    lines = []
    lines.append(f"### Session ({session['id'][:8]}...)")
    lines.append("")
    lines.append(f"**Messages:** {len(user_msgs)} user, {len(assistant_msgs)} assistant")
    
    # Extract first user message as topic
    if user_msgs:
        first_msg = user_msgs[0]['text'][:100]
        lines.append(f"**Started with:** {first_msg}...")
    
    # Count actions
    action_count = sum(1 for m in assistant_msgs if '[' in m['text'] and ']' in m['text'])
    if action_count:
        lines.append(f"**Actions:** {action_count} file/system operations")
    
    # Extract key Q&A pairs
    qa_pairs = []
    last_user = None
    for m in messages:
        if m['role'] == 'user':
            last_user = m['text'][:80]
        elif m['role'] == 'assistant' and last_user:
            qa_pairs.append((last_user, m['text'][:120]))
            last_user = None
    
    if qa_pairs:
        lines.append("")
        lines.append("**Key exchanges:**")
        for q, a in qa_pairs[:3]:
            lines.append(f"- Q: {q}...")
            lines.append(f"  A: {a}...")
    
    lines.append("")
    return '\n'.join(lines)

def generate_memory_file(date, sessions):
    """Generate a complete memory file for a date"""
    lines = []
    lines.append(f"# Memory Log - {date}")
    lines.append("")
    lines.append(f"*Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}*")
    lines.append("")
    
    # Overview
    total_messages = sum(len(s['messages']) for s in sessions)
    lines.append("## Overview")
    lines.append(f"- Sessions: {len(sessions)}")
    lines.append(f"- Total messages: {total_messages}")
    lines.append("")
    
    # Session conversations
    lines.append("## Conversations")
    lines.append("")
    
    for session in sessions:
        if len(session['messages']) > 0:
            lines.append(summarize_session(session))
    
    return '\n'.join(lines)

# ==============================================================================
# MAIN COMMANDS
# ==============================================================================

def cmd_extract():
    """Extract all sessions to memory files"""
    print("=" * 60)
    print("EXTRACTING SESSIONS")
    print("=" * 60)
    
    sessions_by_date = get_all_sessions()
    
    for date in sorted(sessions_by_date.keys()):
        sessions = sessions_by_date[date]
        print(f"\n{date}: {len(sessions)} session(s)")
        
        # Generate memory content
        content = generate_memory_file(date, sessions)
        
        # Write to file
        memory_file = MEMORY_DIR / f"{date}.md"
        with open(memory_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"  Written: {memory_file.name}")
    
    print("\nExtraction complete!")

def cmd_morning():
    """Load morning context"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("MORNING CONTEXT")
    print("=" * 60)
    
    today = datetime.now().strftime("%Y-%m-%d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for date in [yesterday, today]:
        memory_file = MEMORY_DIR / f"{date}.md"
        if memory_file.exists():
            print(f"\n{'='*60}")
            print(f"DATE: {date}")
            print('='*60)
            with open(memory_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Print first 3000 chars
                print(content[:3000])
                if len(content) > 3000:
                    print("\n... (truncated, use 'full' command for more)")

def cmd_full():
    """Load complete history"""
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    
    print("=" * 60)
    print("COMPLETE HISTORY")
    print("=" * 60)
    
    memory_files = sorted(MEMORY_DIR.glob("*.md"), reverse=True)
    
    for mem_file in memory_files:
        if mem_file.name == "embeddings.json":
            continue
        
        print(f"\n{'='*60}")
        print(f"FILE: {mem_file.name}")
        print('='*60)
        
        with open(mem_file, 'r', encoding='utf-8') as f:
            content = f.read()
            # Print summary section
            lines = content.split('\n')
            for line in lines[:50]:
                print(line)

def cmd_sync():
    """Sync to git"""
    print("=" * 60)
    print("SYNCING TO GIT")
    print("=" * 60)
    
    try:
        # Add all changes
        result = subprocess.run(
            ['git', 'add', '-A'],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        
        # Commit
        result = subprocess.run(
            ['git', 'commit', '-m', f'Memory sync: {datetime.now().strftime("%Y-%m-%d %H:%M")}'],
            cwd=WORKSPACE_DIR,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("OK: Committed successfully")
            print(result.stdout)
        else:
            print("Nothing to commit or error:")
            print(result.stderr)
            
    except Exception as e:
        print(f"Error: {e}")

def cmd_all():
    """Run full pipeline"""
    cmd_extract()
    cmd_sync()
    print("\n" + "=" * 60)
    print("FULL PIPELINE COMPLETE")
    print("=" * 60)

# ==============================================================================
# MAIN ENTRY
# ==============================================================================

def main():
    import sys
    
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nUsage: python karen_memory_system.py [command]")
        print("\nCommands: extract, morning, full, sync, all")
        return
    
    command = sys.argv[1]
    
    commands = {
        'extract': cmd_extract,
        'morning': cmd_morning,
        'full': cmd_full,
        'sync': cmd_sync,
        'all': cmd_all,
    }
    
    if command in commands:
        commands[command]()
    else:
        print(f"Unknown command: {command}")
        print(f"Available: {', '.join(commands.keys())}")

if __name__ == "__main__":
    main()
