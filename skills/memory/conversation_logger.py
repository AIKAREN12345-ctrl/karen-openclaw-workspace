#!/usr/bin/env python3
"""
Conversation Logger - SQLite-based conversation history
Works around OpenClaw's EISDIR bug by using custom logging
"""

import sqlite3
import json
import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

class ConversationLogger:
    """
    SQLite-based conversation logger.
    
    Usage:
        logger = ConversationLogger()
        logger.log_message("session_123", "user", "Hello!")
        logger.log_message("session_123", "assistant", "Hi there!")
        
        # Search recent conversations
        results = logger.search_conversations("hello")
        
        # Get full conversation
        history = logger.get_conversation("session_123")
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize the conversation logger.
        
        Args:
            db_path: Path to SQLite database. Defaults to ~/.openclaw/memory/conversations.db
        """
        if db_path is None:
            db_path = Path.home() / ".openclaw" / "memory" / "conversations.db"
        else:
            db_path = Path(db_path).expanduser()
        
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Create tables and indexes if they don't exist."""
        with sqlite3.connect(self.db_path) as conn:
            # Main conversations table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,  -- 'user', 'assistant', 'system'
                    content TEXT NOT NULL,
                    channel TEXT DEFAULT 'telegram',
                    metadata TEXT  -- JSON for extra data
                )
            ''')
            
            # Indexes for fast queries
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON conversations(timestamp)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_session 
                ON conversations(session_id)
            ''')
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_role 
                ON conversations(role)
            ''')
            
            # Full-text search virtual table (FTS5)
            conn.execute('''
                CREATE VIRTUAL TABLE IF NOT EXISTS conversation_fts 
                USING fts5(content, content_rowid=rowid)
            ''')
            
            # Triggers to keep FTS index in sync
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS conversations_ai 
                AFTER INSERT ON conversations BEGIN
                    INSERT INTO conversation_fts(rowid, content) 
                    VALUES (new.id, new.content);
                END
            ''')
            
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS conversations_ad 
                AFTER DELETE ON conversations BEGIN
                    INSERT INTO conversation_fts(conversation_fts, rowid, content) 
                    VALUES ('delete', old.id, old.content);
                END
            ''')
            
            conn.execute('''
                CREATE TRIGGER IF NOT EXISTS conversations_au 
                AFTER UPDATE ON conversations BEGIN
                    INSERT INTO conversation_fts(conversation_fts, rowid, content) 
                    VALUES ('delete', old.id, old.content);
                    INSERT INTO conversation_fts(rowid, content) 
                    VALUES (new.id, new.content);
                END
            ''')
    
    def log_message(self, 
                   session_id: str, 
                   role: str, 
                   content: str, 
                   channel: str = "telegram",
                   metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Log a single message to the database.
        
        Args:
            session_id: Unique identifier for the conversation session
            role: 'user', 'assistant', or 'system'
            content: The message content
            channel: Communication channel (default: 'telegram')
            metadata: Optional dictionary of additional data
            
        Returns:
            The ID of the inserted row
        """
        timestamp = datetime.datetime.now().isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                INSERT INTO conversations (timestamp, session_id, role, content, channel, metadata)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                timestamp,
                session_id,
                role,
                content,
                channel,
                json.dumps(metadata) if metadata else None
            ))
            return cursor.lastrowid
    
    def get_conversation(self, 
                        session_id: str, 
                        limit: int = 100,
                        before_time: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve conversation history for a session.
        
        Args:
            session_id: The session to retrieve
            limit: Maximum number of messages
            before_time: Optional ISO timestamp to get messages before
            
        Returns:
            List of message dictionaries
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            if before_time:
                cursor = conn.execute('''
                    SELECT timestamp, role, content, metadata
                    FROM conversations
                    WHERE session_id = ? AND timestamp < ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, before_time, limit))
            else:
                cursor = conn.execute('''
                    SELECT timestamp, role, content, metadata
                    FROM conversations
                    WHERE session_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (session_id, limit))
            
            rows = cursor.fetchall()
            
            # Convert to list of dicts and parse metadata
            results = []
            for row in reversed(rows):  # Reverse to get chronological order
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                results.append(result)
            
            return results
    
    def search_conversations(self, 
                           query: str, 
                           days: int = 7,
                           limit: int = 20) -> List[Dict[str, Any]]:
        """
        Search conversations using full-text search.
        
        Args:
            query: Search query (supports FTS5 syntax: AND, OR, NOT, "phrase")
            days: Number of days to search back
            limit: Maximum results
            
        Returns:
            List of matching messages
        """
        since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT c.timestamp, c.session_id, c.role, c.content, c.metadata,
                       rank as relevance
                FROM conversation_fts fts
                JOIN conversations c ON fts.rowid = c.id
                WHERE conversation_fts MATCH ? AND c.timestamp > ?
                ORDER BY rank
                LIMIT ?
            ''', (query, since, limit))
            
            rows = cursor.fetchall()
            
            results = []
            for row in rows:
                result = dict(row)
                if result['metadata']:
                    result['metadata'] = json.loads(result['metadata'])
                results.append(result)
            
            return results
    
    def get_recent_sessions(self, days: int = 7) -> List[Dict[str, Any]]:
        """
        Get list of recent conversation sessions with message counts.
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of session summaries
        """
        since = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute('''
                SELECT 
                    session_id,
                    COUNT(*) as message_count,
                    MIN(timestamp) as started,
                    MAX(timestamp) as last_activity
                FROM conversations
                WHERE timestamp > ?
                GROUP BY session_id
                ORDER BY last_activity DESC
            ''', (since,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        with sqlite3.connect(self.db_path) as conn:
            # Total messages
            total = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
            
            # Messages by role
            by_role = {}
            cursor = conn.execute('''
                SELECT role, COUNT(*) as count 
                FROM conversations 
                GROUP BY role
            ''')
            for role, count in cursor.fetchall():
                by_role[role] = count
            
            # Database size
            size = conn.execute('''
                SELECT page_count * page_size 
                FROM pragma_page_count(), pragma_page_size()
            ''').fetchone()[0]
            
            # Date range
            cursor = conn.execute('''
                SELECT MIN(timestamp), MAX(timestamp) FROM conversations
            ''')
            min_ts, max_ts = cursor.fetchone()
            
            return {
                'total_messages': total,
                'by_role': by_role,
                'database_size_bytes': size,
                'database_size_mb': round(size / (1024 * 1024), 2),
                'first_message': min_ts,
                'last_message': max_ts
            }
    
    def export_to_markdown(self, session_id: str, output_path: Optional[str] = None) -> str:
        """
        Export a conversation to markdown format.
        
        Args:
            session_id: Session to export
            output_path: Where to save (default: auto-generated)
            
        Returns:
            Path to the exported file
        """
        messages = self.get_conversation(session_id, limit=10000)
        
        if not messages:
            raise ValueError(f"No messages found for session {session_id}")
        
        if output_path is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = self.db_path.parent / f"export_{session_id}_{timestamp}.md"
        else:
            output_path = Path(output_path)
        
        lines = [
            f"# Conversation Export: {session_id}",
            "",
            f"**Exported:** {datetime.datetime.now().isoformat()}",
            f"**Messages:** {len(messages)}",
            "",
            "---",
            ""
        ]
        
        for msg in messages:
            ts = msg['timestamp'].split('T')[1][:8]  # Extract HH:MM:SS
            role_emoji = "👤" if msg['role'] == 'user' else "🤖" if msg['role'] == 'assistant' else "⚙️"
            lines.append(f"## {ts} {role_emoji} {msg['role'].upper()}")
            lines.append("")
            lines.append(msg['content'])
            lines.append("")
            lines.append("---")
            lines.append("")
        
        output_path.write_text('\n'.join(lines), encoding='utf-8')
        return str(output_path)
    
    def delete_old_conversations(self, days: int = 90) -> int:
        """
        Delete conversations older than specified days.
        
        Args:
            days: Age threshold for deletion
            
        Returns:
            Number of messages deleted
        """
        cutoff = (datetime.datetime.now() - datetime.timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute('''
                DELETE FROM conversations WHERE timestamp < ?
            ''', (cutoff,))
            return cursor.rowcount


def main():
    """CLI interface for testing"""
    import sys
    
    logger = ConversationLogger()
    
    if len(sys.argv) < 2:
        print("Usage: conversation_logger.py <command> [args]")
        print("Commands:")
        print("  log <session_id> <role> <content>  - Log a message")
        print("  get <session_id> [limit]           - Get conversation")
        print("  search <query> [days]              - Search conversations")
        print("  sessions [days]                    - List recent sessions")
        print("  stats                              - Show statistics")
        print("  export <session_id> [output_path]  - Export to markdown")
        return
    
    command = sys.argv[1]
    
    if command == "log" and len(sys.argv) >= 5:
        msg_id = logger.log_message(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Logged message ID: {msg_id}")
    
    elif command == "get" and len(sys.argv) >= 3:
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 100
        messages = logger.get_conversation(sys.argv[2], limit)
        for msg in messages:
            print(f"[{msg['timestamp']}] {msg['role']}: {msg['content'][:100]}...")
    
    elif command == "search" and len(sys.argv) >= 3:
        days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
        results = logger.search_conversations(sys.argv[2], days)
        for r in results:
            print(f"[{r['timestamp']}] {r['session_id']}: {r['content'][:100]}...")
    
    elif command == "sessions":
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
        sessions = logger.get_recent_sessions(days)
        for s in sessions:
            print(f"{s['session_id']}: {s['message_count']} messages (last: {s['last_activity']})")
    
    elif command == "stats":
        stats = logger.get_stats()
        print(json.dumps(stats, indent=2))
    
    elif command == "export" and len(sys.argv) >= 3:
        output = sys.argv[3] if len(sys.argv) > 3 else None
        path = logger.export_to_markdown(sys.argv[2], output)
        print(f"Exported to: {path}")
    
    else:
        print(f"Unknown command or missing arguments: {command}")


if __name__ == "__main__":
    main()
