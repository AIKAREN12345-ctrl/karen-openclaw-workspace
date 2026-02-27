#!/usr/bin/env python3
"""
Session Memory Extractor
Parses OpenClaw session JSONL files and extracts conversation summaries
to add to the memory log for persistent recall.
"""

import json
import re
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path("C:/Users/Karen/.openclaw/agents/main/sessions")
MEMORY_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory")

def parse_session_file(filepath):
    """Parse a session JSONL file and extract conversation"""
    messages = []
    session_date = None
    
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                data = json.loads(line.strip())
                
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
                    
                    # Skip tool results and system messages
                    if role in ('user', 'assistant'):
                        text = extract_text(content)
                        if text and not is_system_noise(text):
                            messages.append({
                                'role': role,
                                'text': text,
                                'timestamp': data.get('timestamp', '')
                            })
            except json.JSONDecodeError:
                continue
    
    return session_date, messages

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
                    # Summarize tool calls
                    name = item.get('name', 'tool')
                    args = item.get('arguments', {})
                    if name == 'read' and 'file_path' in args:
                        texts.append(f"[Read file: {Path(args['file_path']).name}]")
                    elif name == 'write' and 'path' in args:
                        texts.append(f"[Wrote file: {Path(args['path']).name}]")
                    elif name == 'edit' and 'file_path' in args:
                        texts.append(f"[Edited file: {Path(args['file_path']).name}]")
                    elif name == 'exec' and 'command' in args:
                        cmd = args['command'][:50]
                        texts.append(f"[Executed: {cmd}...]")
                    elif name == 'nodes' and 'action' in args:
                        texts.append(f"[Node action: {args['action']}]")
                    else:
                        texts.append(f"[Called {name}]")
        return ' '.join(texts)
    return ''

def is_system_noise(text):
    """Filter out system messages and noise"""
    noise_patterns = [
        r'^\[cron:.*\]',
        r'^Message Ken:',
        r'^Current time:',
        r'^Return your summary',
        r'^Read HEARTBEAT\.md',
        r'An async command you ran earlier',
        r'^System: \[',
        r'HEARTBEAT_OK',
        r'\[System Message\]',
    ]
    for pattern in noise_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def summarize_conversation(messages):
    """Create a summary of the conversation"""
    if not messages:
        return None
    
    # Extract key topics and decisions
    user_msgs = [m['text'] for m in messages if m['role'] == 'user']
    assistant_msgs = [m['text'] for m in messages if m['role'] == 'assistant']
    
    # Look for questions and answers
    qa_pairs = []
    last_user = None
    for m in messages:
        if m['role'] == 'user':
            last_user = m['text'][:100]
        elif m['role'] == 'assistant' and last_user:
            qa_pairs.append((last_user, m['text'][:200]))
            last_user = None
    
    # Build summary
    summary_lines = []
    
    # Count messages
    summary_lines.append(f"**Conversation Length:** {len(user_msgs)} user messages, {len(assistant_msgs)} responses")
    
    # Extract key topics (first user message usually sets the topic)
    if user_msgs:
        first_topic = user_msgs[0][:150]
        summary_lines.append(f"**Started with:** {first_topic}...")
    
    # Look for decisions/actions
    actions = []
    for msg in assistant_msgs:
        if '[Wrote' in msg or '[Edited' in msg or '[Executed' in msg:
            actions.append(msg)
    if actions:
        summary_lines.append(f"**Actions taken:** {len(actions)} file/system operations")
    
    # Sample Q&A
    if qa_pairs:
        summary_lines.append("**Key exchanges:**")
        for q, a in qa_pairs[:3]:  # First 3 Q&A pairs
            summary_lines.append(f"- Q: {q}...")
            summary_lines.append(f"  A: {a}...")
    
    return '\n'.join(summary_lines)

def extract_sessions_to_memory():
    """Main function to extract all sessions to memory files"""
    # Get all session files
    session_files = list(SESSIONS_DIR.glob('*.jsonl'))
    session_files = [f for f in session_files if '.deleted.' not in f.name]
    
    print(f"Found {len(session_files)} session files")
    
    # Group by date
    sessions_by_date = {}
    for filepath in session_files:
        date, messages = parse_session_file(filepath)
        if date and messages:
            if date not in sessions_by_date:
                sessions_by_date[date] = []
            sessions_by_date[date].append({
                'file': filepath.name,
                'messages': messages
            })
    
    # Process each date
    for date in sorted(sessions_by_date.keys()):
        sessions = sessions_by_date[date]
        print(f"\nProcessing {date}: {len(sessions)} session(s)")
        
        # Build memory entry
        memory_lines = [f"\n## Session Conversations - {date}\n"]
        
        for i, session in enumerate(sessions, 1):
            summary = summarize_conversation(session['messages'])
            if summary:
                memory_lines.append(f"\n### Session {i} ({session['file'][:8]}...)\n")
                memory_lines.append(summary)
                memory_lines.append('')
        
        # Append to memory file
        memory_file = MEMORY_DIR / f"{date}.md"
        if memory_file.exists():
            with open(memory_file, 'a', encoding='utf-8') as f:
                f.write('\n'.join(memory_lines))
            print(f"  Appended to {memory_file.name}")
        else:
            # Create new memory file
            with open(memory_file, 'w', encoding='utf-8') as f:
                f.write(f"# Memory Log - {date}\n")
                f.write('\n'.join(memory_lines))
            print(f"  Created {memory_file.name}")
    
    print("\nDone! Regenerate embeddings to make these searchable.")

if __name__ == "__main__":
    extract_sessions_to_memory()
