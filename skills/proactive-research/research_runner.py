# Research Automation Script
# Triggered by cron job every 4 hours
# Uses duckduckgo-search skill via web_fetch

import json
import os
from datetime import datetime
import random

# Research topics rotation
RESEARCH_TOPICS = [
    "AI automation tools small business",
    "OpenClaw updates features",
    "local LLM models comparison",
    "AI tools productivity",
    "memory systems AI",
    "Windows optimization tools",
    "Telegram bot development",
    "GitHub automation workflows",
    "Python automation scripts",
    "Node.js tools 2025"
]

def get_next_topic():
    """Rotate through topics, avoid recent duplicates"""
    tracker_file = "C:\\Users\\Karen\\.openclaw\\workspace\\skills\\proactive-research\\research_tracker.json"
    
    # Load tracker
    if os.path.exists(tracker_file):
        with open(tracker_file, 'r') as f:
            tracker = json.load(f)
    else:
        tracker = {"last_researched": {}, "next_topic_index": 0}
    
    # Get next topic
    topic_index = tracker.get("next_topic_index", 0) % len(RESEARCH_TOPICS)
    topic = RESEARCH_TOPICS[topic_index]
    
    # Update tracker
    tracker["next_topic_index"] = topic_index + 1
    tracker["last_researched"][topic] = datetime.now().isoformat()
    
    # Save tracker
    os.makedirs(os.path.dirname(tracker_file), exist_ok=True)
    with open(tracker_file, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    return topic

def main():
    """Main research function - triggered by cron"""
    topic = get_next_topic()
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
    
    # Log research start
    print(f"[{timestamp}] Starting research on: {topic}")
    
    # The actual research will be done by the agent responding to the cron message
    # This script just sets up the topic rotation
    
    return {
        "topic": topic,
        "timestamp": timestamp,
        "status": "ready"
    }

if __name__ == "__main__":
    result = main()
    print(json.dumps(result, indent=2))
