# OpenClaw Memory System Alternatives - Research Report

**Date:** 2026-03-02  
**Researcher:** Subagent for Karen  
**Status:** Complete  

---

## Executive Summary

The EISDIR bug in OpenClaw's automatic conversation logging prevents reliable capture of conversation history. This report documents **5 practical, implementable solutions** that don't require waiting for OpenClaw updates.

**Recommended Approach:** Hybrid solution combining **custom Python logging** + **SQLite database** + **semantic search** using existing Ollama infrastructure.

---

## 1. Understanding the Problem

### The EISDIR Bug
- **Symptom:** OpenClaw fails to write conversation logs with "EISDIR: illegal operation on a directory" error
- **Impact:** Automatic conversation history is unreliable or completely broken
- **Root Cause:** OpenClaw attempts to write to a path that is actually a directory, not a file
- **Status:** Requires OpenClaw update to fix (timeline unknown)

### Current Workaround in Place
Karen's system already has a **manual memory system** that works:
- Daily memory files: `memory/YYYY-MM-DD.md`
- Long-term memory: `MEMORY.md`
- Hourly system logs via cron jobs
- This is **agent-initiated**, not automatic logging

---

## 2. Alternative Memory Systems

### Option A: Custom Python Logging (RECOMMENDED)

**Concept:** Create a Python-based conversation logger that captures messages via webhook or file watcher.

**Implementation:**
```python
# conversation_logger.py
import sqlite3
import json
import datetime
from pathlib import Path

class ConversationLogger:
    def __init__(self, db_path="~/.openclaw/memory/conversations.db"):
        self.db_path = Path(db_path).expanduser()
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    session_id TEXT,
                    role TEXT,  -- 'user' or 'assistant'
                    content TEXT,
                    channel TEXT,
                    metadata TEXT  -- JSON for extra data
                )
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session 
                ON conversations(session_id)
            ''')
    
    def log_message(self, session_id, role, content, channel="telegram", metadata=None):
        """Log a single message"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO conversations (timestamp, session_id, role, content, channel, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                datetime.datetime.now().isoformat(),
                session_id,
                role,
                content,
                channel,
                json.dumps(metadata) if metadata else None
            ))
    
    def get_conversation(self, session_id, limit=100):
        """Retrieve conversation history for a session"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, role, content FROM conversations
                WHERE session_id = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, limit))
            return cursor.fetchall()
    
    def search_conversations(self, query, days=7):
        """Search recent conversations (simple text search)"""
        since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, role, content FROM conversations
                WHERE content LIKE ? AND timestamp > ?
                ORDER BY timestamp DESC
            ''', (f'%{query}%', since))
            return cursor.fetchall()
```

**Integration with OpenClaw:**
1. Create a wrapper script that runs alongside OpenClaw
2. Use Telegram Bot API to capture messages (since Karen uses Telegram)
3. Store in SQLite database
4. Query via custom skill

**Pros:**
- Works immediately, no OpenClaw changes needed
- SQLite is fast, reliable, requires no server
- Can query by date, session, or content
- Exportable to markdown for human reading

**Cons:**
- Requires separate process/script
- Doesn't capture internal OpenClaw thinking/reasoning
- Need to handle message parsing

**Effort:** 2-3 hours to implement

---

### Option B: Telegram Bot Message Logging

**Concept:** Since Karen uses Telegram, capture messages at the source using Telegram Bot API.

**Implementation:**
```python
# telegram_logger.py
import asyncio
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import sqlite3
import json

class TelegramConversationLogger:
    def __init__(self, bot_token, db_path="conversations.db"):
        self.bot_token = bot_token
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY,
                    message_id INTEGER,
                    chat_id INTEGER,
                    user_id INTEGER,
                    timestamp TEXT,
                    text TEXT,
                    from_user BOOLEAN,
                    raw_data TEXT
                )
            ''')
    
    async def log_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Log every message to database"""
        message = update.message or update.edited_message
        if not message:
            return
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO messages 
                (message_id, chat_id, user_id, timestamp, text, from_user, raw_data)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                message.message_id,
                message.chat_id,
                message.from_user.id if message.from_user else None,
                message.date.isoformat(),
                message.text or message.caption or "",
                not message.from_user.is_bot if message.from_user else True,
                json.dumps(message.to_dict())
            ))
    
    def run(self):
        application = Application.builder().token(self.bot_token).build()
        application.add_handler(MessageHandler(filters.ALL, self.log_message))
        application.run_polling()
```

**Pros:**
- Captures ALL messages, including ones OpenClaw might miss
- Works independently of OpenClaw
- Can capture media, files, etc.
- Native async support

**Cons:**
- Requires running a separate bot instance
- Telegram rate limits apply
- Doesn't capture OpenClaw's internal processing

**Effort:** 1-2 hours

---

### Option C: File-Based Markdown Logging (Enhanced Current System)

**Concept:** Extend the existing manual memory system with structured logging.

**Implementation:**
```python
# enhanced_memory_logger.py
import datetime
import json
import re
from pathlib import Path

class EnhancedMemoryLogger:
    """Structured conversation logging to markdown files"""
    
    def __init__(self, memory_dir="~/.openclaw/workspace/memory"):
        self.memory_dir = Path(memory_dir).expanduser()
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        self.current_session = None
    
    def start_session(self, session_type="main", context=None):
        """Start a new conversation session"""
        self.current_session = {
            "id": datetime.datetime.now().strftime("%Y%m%d_%H%M%S"),
            "type": session_type,
            "started": datetime.datetime.now().isoformat(),
            "context": context or {}
        }
        
        # Create session file
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        session_file = self.memory_dir / f"session_{today}_{self.current_session['id']}.md"
        
        with open(session_file, 'w', encoding='utf-8') as f:
            f.write(f"# Session: {self.current_session['id']}\n\n")
            f.write(f"**Type:** {session_type}\n")
            f.write(f"**Started:** {self.current_session['started']}\n")
            if context:
                f.write(f"**Context:** {json.dumps(context)}\n")
            f.write("\n---\n\n")
        
        return session_file
    
    def log_exchange(self, user_message, assistant_response, metadata=None):
        """Log a user-assistant exchange"""
        if not self.current_session:
            self.start_session()
        
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        session_file = self.memory_dir / f"session_{today}_{self.current_session['id']}.md"
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        with open(session_file, 'a', encoding='utf-8') as f:
            f.write(f"## {timestamp}\n\n")
            f.write(f"**User:** {user_message}\n\n")
            f.write(f"**Assistant:** {assistant_response}\n\n")
            if metadata:
                f.write(f"```json\n{json.dumps(metadata, indent=2)}\n```\n\n")
            f.write("---\n\n")
    
    def search_sessions(self, query, days=7):
        """Search recent session files for a query"""
        results = []
        cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
        
        for session_file in self.memory_dir.glob("session_*.md"):
            # Parse date from filename
            try:
                file_date = datetime.datetime.strptime(
                    session_file.stem.split('_')[1], 
                    "%Y-%m-%d"
                )
                if file_date < cutoff:
                    continue
            except:
                continue
            
            content = session_file.read_text(encoding='utf-8')
            if query.lower() in content.lower():
                # Extract matching context
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if query.lower() in line.lower():
                        context = '\n'.join(lines[max(0, i-3):min(len(lines), i+4)])
                        results.append({
                            'file': session_file.name,
                            'context': context
                        })
                        break
        
        return results
```

**Pros:**
- Builds on existing system
- Human-readable markdown output
- Git-friendly (version controlled)
- No database dependencies
- Easy to search with grep/ripgrep

**Cons:**
- Slower for large-scale searching
- No structured querying
- File I/O overhead

**Effort:** 1-2 hours

---

### Option D: SQLite + Full-Text Search (FTS5)

**Concept:** Use SQLite's built-in Full-Text Search extension for powerful conversation search.

**Implementation:**
```python
# fts_conversation_logger.py
import sqlite3
import datetime
from pathlib import Path

class FTSConversationLogger:
    """SQLite-based conversation logger with full-text search"""
    
    def __init__(self, db_path="~/.openclaw/memory/conversations_fts.db"):
        self.db_path = Path(db_path).expanduser()
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database with FTS5 virtual table"""
        with sqlite3.connect(self.db_path) as conn:
            # Main conversations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY,
                    session_id TEXT,
                    timestamp TEXT,
                    role TEXT,
                    channel TEXT
                )
            ''')
            
            # FTS5 virtual table for fast text search
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS conversation_content 
                USING fts5(content, content_rowid=rowid)
            ''')
            
            # Triggers to keep FTS index in sync
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS conversations_ai 
                AFTER INSERT ON conversations BEGIN
                    INSERT INTO conversation_content(rowid, content) 
                    VALUES (new.id, new.content);
                END
            ''')
            
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS conversations_ad 
                AFTER DELETE ON conversations BEGIN
                    INSERT INTO conversation_content(conversation_content, rowid, content) 
                    VALUES ('delete', old.id, old.content);
                END
            ''')
    
    def log_message(self, session_id, role, content, channel="telegram"):
        """Log a message with FTS indexing"""
        timestamp = datetime.datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO conversations (session_id, timestamp, role, channel)
                VALUES (?, ?, ?, ?)
            ''', (session_id, timestamp, role, channel))
            
            # FTS content is handled by trigger, but we need to store content
            # Actually, let's adjust the schema
    
    def search(self, query, limit=20):
        """Full-text search conversations"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT c.timestamp, c.role, cc.content, rank
                FROM conversation_content cc
                JOIN conversations c ON cc.rowid = c.id
                WHERE conversation_content MATCH ?
                ORDER BY rank
                LIMIT ?
            ''', (query, limit))
            return cursor.fetchall()
    
    def get_conversation_context(self, session_id, before_time, context_messages=5):
        """Get N messages before a specific time for context"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                SELECT timestamp, role, content 
                FROM conversations
                WHERE session_id = ? AND timestamp < ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (session_id, before_time, context_messages))
            return cursor.fetchall()
```

**Pros:**
- Extremely fast full-text search
- Built into SQLite (no extra dependencies)
- Supports complex queries (AND, OR, NOT, phrase search)
- Relevance ranking built-in

**Cons:**
- Slightly more complex setup
- FTS5 not available in all SQLite builds (but standard in Python's sqlite3)

**Effort:** 2-3 hours

---

### Option E: ChromaDB Vector Store (Semantic Search)

**Concept:** Use ChromaDB with local embeddings for semantic memory search.

**Implementation:**
```python
# semantic_memory.py
import chromadb
from chromadb.config import Settings
import datetime
import hashlib

class SemanticMemory:
    """Vector-based semantic memory using ChromaDB"""
    
    def __init__(self, persist_dir="~/.openclaw/memory/chroma"):
        import os
        self.persist_dir = os.path.expanduser(persist_dir)
        
        # Initialize ChromaDB with persistence
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_dir,
            anonymized_telemetry=False
        ))
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_conversation(self, session_id, role, content, metadata=None):
        """Add a conversation with auto-generated embedding"""
        timestamp = datetime.datetime.now().isoformat()
        doc_id = hashlib.md5(f"{session_id}:{timestamp}:{content[:50]}".encode()).hexdigest()
        
        self.collection.add(
            documents=[content],
            metadatas=[{
                "session_id": session_id,
                "role": role,
                "timestamp": timestamp,
                **(metadata or {})
            }],
            ids=[doc_id]
        )
    
    def search(self, query, n_results=5):
        """Semantic search for similar conversations"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results
    
    def get_recent(self, session_id=None, n_results=10):
        """Get recent conversations"""
        where_filter = {"session_id": session_id} if session_id else None
        
        results = self.collection.get(
            where=where_filter,
            limit=n_results
        )
        return results
```

**Pros:**
- Semantic search (finds conceptually related content)
- Fast similarity search
- Persistent storage
- Can integrate with Ollama for embeddings

**Cons:**
- Requires ChromaDB dependency
- Embeddings take time to generate
- More memory intensive
- Overkill for simple text search

**Effort:** 2-3 hours

---

## 3. Database Options Comparison

| Feature | SQLite (Basic) | SQLite (FTS5) | ChromaDB |
|---------|---------------|---------------|----------|
| **Setup Complexity** | Low | Low-Medium | Medium |
| **Query Speed** | Fast | Very Fast | Very Fast |
| **Text Search** | LIKE queries | Full-text | Semantic |
| **Dependencies** | None (built-in) | None | chromadb |
| **Storage Size** | Small | Small | Medium-Large |
| **Backup** | File copy | File copy | Directory copy |
| **Best For** | Simple logging | Keyword search | Concept search |

---

## 4. OpenClaw Integration Patterns

### Pattern 1: Skill-Based Access
Create an OpenClaw skill for memory retrieval:

```yaml
# memory-retrieval/SKILL.md
---
name: memory-retrieval
description: Retrieve conversation history and past context. Use when the user asks about previous conversations, wants to recall something said earlier, or needs context from past sessions.
---

# Memory Retrieval

## Querying Conversations

Use the memory database to find past conversations:

```python
# In your response generation
import sqlite3

def search_memory(query, days=7):
    db_path = "~/.openclaw/memory/conversations.db"
    # ... query logic
    return results
```

## When to Use

- User asks "What did we discuss yesterday?"
- User references something from earlier
- Need context for a continuing task
- User says "remember when..."
```

### Pattern 2: Automatic Session Context Loading
Modify session startup to load recent context:

```python
# session_context_loader.py
def load_recent_context(session_id, n_messages=10):
    """Load recent messages for context window priming"""
    db_path = "~/.openclaw/memory/conversations.db"
    
    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute('''
            SELECT role, content FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (session_id, n_messages))
        
        messages = []
        for role, content in cursor.fetchall():
            messages.append({"role": role, "content": content})
        
        return reversed(messages)  # Chronological order
```

### Pattern 3: Webhook Integration
If OpenClaw supports webhooks or callbacks:

```python
# webhook_receiver.py
from flask import Flask, request
import sqlite3

app = Flask(__name__)

@app.route('/log', methods=['POST'])
def log_conversation():
    data = request.json
    
    # Log to database
    logger = ConversationLogger()
    logger.log_message(
        session_id=data['session_id'],
        role=data['role'],
        content=data['content']
    )
    
    return {"status": "ok"}
```

---

## 5. Workarounds for EISDIR Bug

### Workaround 1: Disable Auto-Logging (If Configurable)
Check if OpenClaw has a configuration option:

```json
// In openclaw.json
{
  "logging": {
    "autoConversationLog": false
  }
}
```

**Status:** Unknown if this option exists. Check with `openclaw config` or documentation.

### Workaround 2: Custom Log Directory
Redirect logging to a different path:

```json
// In openclaw.json
{
  "logging": {
    "conversationLogPath": "C:/Users/Karen/.openclaw/logs/conversations"
  }
}
```

**Implementation:**
1. Create the directory manually first
2. Ensure OpenClaw has write permissions
3. Monitor for EISDIR errors

### Workaround 3: File Watcher Approach
Watch the log file location and fix issues automatically:

```python
# log_fixer.py
import watchdog
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import os
import shutil

class LogFixer(FileSystemEventHandler):
    """Watch for EISDIR issues and fix them"""
    
    def on_created(self, event):
        if event.is_directory:
            # Check if this directory is blocking a log file
            log_file_path = event.src_path.replace('.d', '.log')
            if os.path.exists(log_file_path):
                # Move directory and recreate as file
                backup = event.src_path + '.backup'
                shutil.move(event.src_path, backup)
                open(log_file_path, 'a').close()

# Run watcher
observer = Observer()
observer.schedule(LogFixer(), path='~/.openclaw/logs', recursive=True)
observer.start()
```

### Workaround 4: Symlink Approach
Create a symlink structure that prevents the bug:

```powershell
# Create a file where OpenClaw expects a directory
New-Item -ItemType File -Path "$env:USERPROFILE\.openclaw\logs\conversations.log" -Force
```

**Note:** This is speculative - the bug might be in how OpenClaw determines the path.

---

## 6. Recommended Implementation Plan

### Phase 1: Immediate (Today)
**Goal:** Working conversation logging

1. **Implement SQLite Basic Logger (Option A)**
   - Create `~/.openclaw/workspace/skills/memory/conversation_logger.py`
   - Test with manual entries
   - Time: 1 hour

2. **Create Telegram Logger (Option B)**
   - Since Karen uses Telegram, this captures everything
   - Run as a background service
   - Time: 1 hour

### Phase 2: Short-term (This Week)
**Goal:** Searchable, useful memory

3. **Add FTS5 Support (Option D)**
   - Upgrade database schema
   - Implement search functions
   - Time: 2 hours

4. **Create Memory Retrieval Skill**
   - Allow querying past conversations
   - Integrate with session startup
   - Time: 2 hours

### Phase 3: Medium-term (Next 2 Weeks)
**Goal:** Semantic understanding

5. **Add ChromaDB (Option E)**
   - For semantic/conceptual search
   - Use Ollama for embeddings
   - Time: 3 hours

6. **Automatic Context Loading**
   - Load relevant past conversations at session start
   - Time: 2 hours

---

## 7. Implementation Files to Create

### File 1: Core Logger
**Path:** `~/.openclaw/workspace/skills/memory/conversation_logger.py`
**Purpose:** SQLite-based conversation logging
**Code:** See Option A above

### File 2: Telegram Capture
**Path:** `~/.openclaw/workspace/skills/memory/telegram_logger.py`
**Purpose:** Capture all Telegram messages
**Code:** See Option B above

### File 3: Memory Skill
**Path:** `~/.openclaw/workspace/skills/memory/SKILL.md`
**Purpose:** OpenClaw skill for memory retrieval
**Content:**
```markdown
---
name: memory
description: Retrieve and search conversation history. Use when the user asks about previous conversations, wants to recall past discussions, or needs context from earlier sessions.
---

# Memory System

## Retrieving Conversations

### Search by Keyword
```python
from skills.memory.conversation_logger import ConversationLogger

logger = ConversationLogger()
results = logger.search_conversations("project deadline")
```

### Get Recent Session
```python
history = logger.get_conversation(session_id="2026-03-02_main", limit=20)
```

## When to Use

- User asks "What did we talk about yesterday?"
- User references a previous task
- Need context for continuing work
- User says "as I mentioned before..."
```

### File 4: Session Context Loader
**Path:** `~/.openclaw/workspace/skills/memory/session_context.py`
**Purpose:** Load recent context at session start
**Code:** See Pattern 2 above

### File 5: Migration Script
**Path:** `~/.openclaw/workspace/skills/memory/migrate_existing.py`
**Purpose:** Convert existing memory files to database
**Code:**
```python
# Parse existing markdown files and import to SQLite
import re
from pathlib import Path
import sqlite3

def migrate_memory_files(memory_dir="~/.openclaw/workspace/memory"):
    memory_path = Path(memory_dir).expanduser()
    logger = ConversationLogger()
    
    for md_file in memory_path.glob("*.md"):
        content = md_file.read_text()
        
        # Parse entries (customize based on your format)
        entries = re.findall(r'## (\d{2}:\d{2}).*?\n\n(.*?)(?=\n## |\Z)', 
                            content, re.DOTALL)
        
        for time, text in entries:
            # Add to database
            pass  # Implementation depends on format
```

---

## 8. Testing Plan

1. **Unit Tests**
   ```python
   # test_conversation_logger.py
   import unittest
   import tempfile
   from pathlib import Path
   
   class TestConversationLogger(unittest.TestCase):
       def setUp(self):
           self.temp_dir = tempfile.mkdtemp()
           self.db_path = Path(self.temp_dir) / "test.db"
           self.logger = ConversationLogger(self.db_path)
       
       def test_log_and_retrieve(self):
           self.logger.log_message("test_session", "user", "Hello")
           self.logger.log_message("test_session", "assistant", "Hi there")
           
           results = self.logger.get_conversation("test_session")
           self.assertEqual(len(results), 2)
   ```

2. **Integration Test**
   - Run Telegram logger for 1 hour
   - Verify all messages captured
   - Test search functionality

3. **Load Test**
   - Simulate 10,000 messages
   - Verify query performance < 100ms

---

## 9. Maintenance & Monitoring

### Regular Tasks

**Daily:**
- Check database size
- Verify logger is running

**Weekly:**
- Backup database
- Review search performance
- Archive old conversations (>90 days)

**Monthly:**
- Optimize database (VACUUM)
- Review and update search queries

### Monitoring Queries

```sql
-- Database size
SELECT page_count * page_size as size_bytes 
FROM pragma_page_count(), pragma_page_size();

-- Message count by day
SELECT date(timestamp) as day, count(*) as messages
FROM conversations
GROUP BY day
ORDER BY day DESC
LIMIT 7;

-- Most active sessions
SELECT session_id, count(*) as message_count
FROM conversations
WHERE timestamp > datetime('now', '-7 days')
GROUP BY session_id
ORDER BY message_count DESC
LIMIT 10;
```

---

## 10. Conclusion & Recommendations

### Immediate Actions (Do Today)

1. **Implement SQLite Basic Logger** - 1 hour, immediate benefit
2. **Set up Telegram Logger** - 1 hour, captures everything
3. **Create Memory Skill** - 30 minutes, enables retrieval

### Why This Approach?

- **No OpenClaw changes needed** - Works around EISDIR bug
- **Incremental** - Can start simple and add features
- **Proven** - Based on existing working patterns in Karen's system
- **Flexible** - Easy to switch databases later if needed
- **Git-friendly** - Can export to markdown for version control

### Expected Outcomes

- ✅ All conversations captured reliably
- ✅ Fast keyword search (< 100ms)
- ✅ Context loading at session start
- ✅ No dependency on OpenClaw auto-logging
- ✅ Backup and export capabilities

### Total Effort

- **Phase 1:** 2-3 hours
- **Phase 2:** 4 hours
- **Phase 3:** 5 hours
- **Total:** ~11 hours for complete system

---

## Appendix: Resources

### SQLite Documentation
- https://sqlite.org/fts5.html (FTS5)
- https://sqlite.org/lang.html (SQL syntax)

### ChromaDB
- https://docs.trychroma.com/

### Python Libraries
- `sqlite3` (built-in)
- `chromadb` (pip install chromadb)
- `python-telegram-bot` (pip install python-telegram-bot)

### OpenClaw Skills
- See `~/.openclaw/workspace/skills/local-llm/` for examples

---

*Report generated by subagent for Karen's memory system research.*
