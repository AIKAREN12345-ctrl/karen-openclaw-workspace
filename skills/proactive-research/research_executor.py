#!/usr/bin/env python3
"""
Research Executor - Called by subagent to perform actual research
Usage: python research_executor.py <topic_id>
"""

import sys
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

RESEARCH_DIR = Path("C:/Users/Karen/.openclaw/workspace/memory/research")
STATE_FILE = Path("C:/Users/Karen/.openclaw/workspace/memory/research-state.json")

def load_state():
    with open(STATE_FILE, 'r') as f:
        return json.load(f)

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def is_due(topic, now):
    if topic['lastResearched'] is None:
        return True
    
    last = datetime.fromisoformat(topic['lastResearched'].replace('Z', '+00:00'))
    freq = topic['frequency']
    
    if freq == 'daily':
        return (now - last) >= timedelta(days=1)
    elif freq == 'weekly':
        return (now - last) >= timedelta(weeks=1)
    elif freq == 'hourly':
        return (now - last) >= timedelta(hours=1)
    return False

def get_due_topics():
    state = load_state()
    now = datetime.utcnow()
    
    due = []
    for topic in state['topics']:
        if is_due(topic, now):
            due.append(topic)
    
    # Sort by priority
    priority_order = {'high': 0, 'medium': 1, 'low': 2}
    due.sort(key=lambda x: priority_order.get(x['priority'], 99))
    
    return due

def mark_researched(topic_id):
    state = load_state()
    for topic in state['topics']:
        if topic['id'] == topic_id:
            topic['lastResearched'] = datetime.utcnow().isoformat() + 'Z'
            break
    save_state(state)

def get_output_path(topic_id):
    date_str = datetime.utcnow().strftime('%Y-%m-%d')
    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    return RESEARCH_DIR / f"{date_str}_{topic_id}.md"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # List due topics
        due = get_due_topics()
        print(json.dumps([t['id'] for t in due]))
        sys.exit(0)
    
    topic_id = sys.argv[1]
    output_path = get_output_path(topic_id)
    
    # Mark as researched
    mark_researched(topic_id)
    
    print(f"Research topic: {topic_id}")
    print(f"Output: {output_path}")
    print("READY_FOR_RESEARCH")
