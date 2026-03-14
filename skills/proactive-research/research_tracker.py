#!/usr/bin/env python3
"""
Proactive Research Rotation System
Tracks what we've researched to avoid duplication
"""

import json
import random
from datetime import datetime, timedelta
from pathlib import Path

class ResearchTracker:
    def __init__(self):
        self.tracker_file = Path.home() / ".openclaw" / "workspace" / "memory" / "research_tracker.json"
        self.topics = [
            {
                "id": "openclaw_updates",
                "name": "OpenClaw Releases & Features",
                "query": "OpenClaw 2026.3 latest release March 2026 github",
                "sources": ["github.com/openclaw/openclaw/releases", "docs.openclaw.ai"],
                "frequency": "daily",
                "last_researched": None,
                "priority": "high",
                "date_sensitive": True
            },
            {
                "id": "local_llm_models",
                "name": "Local LLM Model Updates",
                "query": "best local LLM 2026 qwen2.5 llama3.2 March benchmark performance",
                "sources": ["ollama.com/library", "huggingface.co", "reddit.com/r/LocalLLaMA"],
                "frequency": "weekly",
                "last_researched": None,
                "priority": "medium",
                "date_sensitive": True
            },
            {
                "id": "ai_tools",
                "name": "AI Tools & Automation",
                "query": "new AI tools March 2026 automation productivity releases",
                "sources": ["producthunt.com", "github.com/trending", "news.ycombinator.com"],
                "frequency": "weekly",
                "last_researched": None,
                "priority": "medium",
                "date_sensitive": True
            },
            {
                "id": "windows_optimization",
                "name": "Windows 11 Optimization",
                "query": "Windows 11 optimization tips performance 2025",
                "frequency": "weekly",
                "last_researched": None,
                "priority": "low"
            },
            {
                "id": "security_alerts",
                "name": "Security Alerts & Patches",
                "query": "security vulnerability March 2026 Windows OpenClaw CVE patch",
                "sources": ["cve.mitre.org", "security.googleblog.com", "msrc.microsoft.com"],
                "frequency": "daily",
                "last_researched": None,
                "priority": "high",
                "date_sensitive": True
            },
            {
                "id": "telegram_bots",
                "name": "Telegram Bot Features",
                "query": "Telegram bot API new features automation 2025",
                "frequency": "weekly",
                "last_researched": None,
                "priority": "low"
            },
            {
                "id": "memory_systems",
                "name": "AI Memory Systems",
                "query": "AI agent memory systems RAG vector databases 2025",
                "frequency": "weekly",
                "last_researched": None,
                "priority": "medium"
            }
        ]
        self.load_tracker()
    
    def load_tracker(self):
        """Load research history"""
        if self.tracker_file.exists():
            with open(self.tracker_file, 'r') as f:
                data = json.load(f)
                for topic in self.topics:
                    if topic['id'] in data:
                        topic['last_researched'] = data[topic['id']]
    
    def save_tracker(self):
        """Save research history"""
        data = {t['id']: t['last_researched'] for t in self.topics}
        with open(self.tracker_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def get_next_topic(self):
        """Get the next topic that needs research"""
        now = datetime.now()
        candidates = []
        
        for topic in self.topics:
            if topic['last_researched'] is None:
                candidates.append(topic)
            else:
                last = datetime.fromisoformat(topic['last_researched'])
                if topic['frequency'] == 'daily':
                    if now - last > timedelta(days=1):
                        candidates.append(topic)
                elif topic['frequency'] == 'weekly':
                    if now - last > timedelta(days=7):
                        candidates.append(topic)
        
        if not candidates:
            return None
        
        # Sort by priority and pick highest
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        candidates.sort(key=lambda x: priority_order[x['priority']])
        
        return candidates[0]
    
    def mark_researched(self, topic_id):
        """Mark a topic as researched"""
        for topic in self.topics:
            if topic['id'] == topic_id:
                topic['last_researched'] = datetime.now().isoformat()
                break
        self.save_tracker()
    
    def get_research_plan(self):
        """Get today's research plan"""
        topic = self.get_next_topic()
        if not topic:
            return None
        
        return {
            'topic_id': topic['id'],
            'name': topic['name'],
            'query': topic['query'],
            'frequency': topic['frequency']
        }

def main():
    """Main entry point"""
    tracker = ResearchTracker()
    plan = tracker.get_research_plan()
    
    if plan:
        print(f"RESEARCH_TASK:{json.dumps(plan)}")
    else:
        print("NO_RESEARCH_NEEDED")

if __name__ == "__main__":
    main()
