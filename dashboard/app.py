import os
import json
import subprocess
import psutil
import sqlite3
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
from flask_login import LoginManager, UserMixin, login_required, login_user, logout_user
import threading
import time

# Get OpenClaw path
OPENCLAW_CMD = os.path.expanduser('~/.openclaw/bin/openclaw.cmd')
if not os.path.exists(OPENCLAW_CMD):
    OPENCLAW_CMD = 'openclaw'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'karen-dashboard-secret-key-change-in-production'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')
login_manager = LoginManager()
login_manager.init_app(app)

# Database setup
DB_PATH = os.path.expanduser('~/.openclaw/workspace/dashboard/data/dashboard.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Projects table
    c.execute('''CREATE TABLE IF NOT EXISTS projects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        status TEXT DEFAULT 'active',
        priority TEXT DEFAULT 'medium',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        due_date TIMESTAMP,
        tags TEXT,
        notes TEXT
    )''')
    
    # Research history table
    c.execute('''CREATE TABLE IF NOT EXISTS research_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        topic TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        results_file TEXT,
        model_used TEXT,
        summary TEXT
    )''')
    
    # Notifications table
    c.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        message TEXT,
        type TEXT DEFAULT 'info',
        read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # System events table
    c.execute('''CREATE TABLE IF NOT EXISTS system_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_type TEXT,
        message TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Activity log table
    c.execute('''CREATE TABLE IF NOT EXISTS activity_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        action TEXT NOT NULL,
        details TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Add favorite column to projects if not exists
    try:
        c.execute('ALTER TABLE projects ADD COLUMN favorite BOOLEAN DEFAULT 0')
    except:
        pass  # Column already exists
    
    # Pomodoro sessions table
    c.execute('''CREATE TABLE IF NOT EXISTS pomodoro_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        project_id INTEGER,
        duration INTEGER DEFAULT 25,
        completed BOOLEAN DEFAULT 0,
        started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (project_id) REFERENCES projects(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

# Simple user store
USERS = {
    'admin': {'password': 'karen2026', 'name': 'Administrator'},
    'ken': {'password': 'karen2026', 'name': 'Ken'}
}

class User(UserMixin):
    def __init__(self, username):
        self.id = username
        self.name = USERS[username]['name']

@login_manager.user_loader
def load_user(user_id):
    if user_id in USERS:
        return User(user_id)
    return None

# Background task for real-time updates
def background_monitor():
    while True:
        try:
            socketio.emit('system_update', get_system_data())
            time.sleep(5)
        except:
            time.sleep(5)

def get_system_data():
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    cpu_percent = psutil.cpu_percent(interval=0.1)
    
    return {
        'cpu_percent': cpu_percent,
        'memory': {
            'total_gb': round(memory.total / (1024**3), 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'percent': memory.percent
        },
        'disk': {
            'total_gb': round(disk.total / (1024**3), 2),
            'free_gb': round(disk.free / (1024**3), 2),
            'percent': round((disk.used / disk.total) * 100, 1)
        },
        'timestamp': datetime.now().isoformat()
    }

# Start background monitor
monitor_thread = threading.Thread(target=background_monitor, daemon=True)
monitor_thread.start()

# Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if username in USERS and USERS[username]['password'] == password:
        user = User(username)
        login_user(user)
        return jsonify({'success': True, 'name': user.name})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/logout')
@login_required
def logout():
    logout_user()
    return jsonify({'success': True})

# System Status API
@app.route('/api/status')
@login_required
def api_status():
    try:
        result = subprocess.run(
            [OPENCLAW_CMD, 'status', '--json'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )
        openclaw_status = json.loads(result.stdout) if result.returncode == 0 else {}
    except:
        openclaw_status = {'error': 'Unable to fetch OpenClaw status'}
    
    try:
        result = subprocess.run(
            ['ollama', 'list'],
            capture_output=True,
            text=True,
            timeout=5,
            shell=True
        )
        ollama_models = result.stdout.strip().split('\n')[1:] if result.returncode == 0 else []
    except:
        ollama_models = []
    
    return jsonify({
        'timestamp': datetime.now().isoformat(),
        'openclaw': openclaw_status,
        'system': get_system_data(),
        'ollama': {
            'models': ollama_models,
            'status': 'running' if ollama_models else 'error'
        }
    })

# Projects API
@app.route('/api/projects', methods=['GET'])
@login_required
def get_projects():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM projects ORDER BY updated_at DESC')
    projects = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'projects': projects})

@app.route('/api/projects', methods=['POST'])
@login_required
def create_project():
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''INSERT INTO projects (title, description, status, priority, due_date, tags, notes)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              (data.get('title'), data.get('description'), data.get('status', 'active'),
               data.get('priority', 'medium'), data.get('due_date'), data.get('tags'), data.get('notes')))
    conn.commit()
    project_id = c.lastrowid
    conn.close()
    
    socketio.emit('project_created', {'id': project_id})
    return jsonify({'success': True, 'id': project_id})

@app.route('/api/projects/<int:project_id>', methods=['PUT'])
@login_required
def update_project(project_id):
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''UPDATE projects SET title=?, description=?, status=?, priority=?,
                 due_date=?, tags=?, notes=?, updated_at=CURRENT_TIMESTAMP WHERE id=?''',
              (data.get('title'), data.get('description'), data.get('status'),
               data.get('priority'), data.get('due_date'), data.get('tags'), data.get('notes'), project_id))
    conn.commit()
    conn.close()
    
    socketio.emit('project_updated', {'id': project_id})
    return jsonify({'success': True})

@app.route('/api/projects/<int:project_id>', methods=['DELETE'])
@login_required
def delete_project(project_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('DELETE FROM projects WHERE id=?', (project_id,))
    conn.commit()
    conn.close()
    
    socketio.emit('project_deleted', {'id': project_id})
    return jsonify({'success': True})

@app.route('/api/projects/<int:project_id>/move', methods=['POST'])
@login_required
def move_project(project_id):
    data = request.json
    new_status = data.get('status')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE projects SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?',
              (new_status, project_id))
    conn.commit()
    conn.close()
    
    socketio.emit('project_moved', {'id': project_id, 'status': new_status})
    return jsonify({'success': True})

# Research API
@app.route('/api/research/history', methods=['GET'])
@login_required
def get_research_history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM research_history ORDER BY started_at DESC LIMIT 50')
    history = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'history': history})

@app.route('/api/research/trigger', methods=['POST'])
@login_required
def trigger_research():
    data = request.json
    topic = data.get('topic', 'general')
    
    topic_map = {
        'openclaw': 'OpenClaw updates',
        'ai-models': 'AI model releases',
        'income': 'AI income opportunities',
        'philosophy': 'Philosophy/personal growth',
        'tech-news': 'Tech news',
        'open-source': 'Open source releases',
        'industry': 'Industry moves',
        'dev-tools': 'Developer tools',
        'hardware': 'Hardware/GPU news',
        'deep-dive': 'Deep dive analysis',
        'ai-safety': 'AI safety/policy',
        'kdp': 'KDP coloring books'
    }
    
    research_title = topic_map.get(topic, 'General research')
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO research_history (topic, status, model_used) VALUES (?, ?, ?)',
              (research_title, 'running', 'kimi-coding/k2p5'))
    research_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Spawn research subagent
    try:
        subprocess.Popen(
            [OPENCLAW_CMD, 'sessions', 'spawn',
             '--task', f'Research {research_title} using web_fetch',
             '--model', 'kimi-coding/k2p5',
             '--mode', 'run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    socketio.emit('research_started', {'id': research_id, 'topic': research_title})
    return jsonify({'success': True, 'id': research_id, 'topic': research_title})

# Calendar API
@app.route('/api/calendar/events', methods=['GET'])
@login_required
def get_calendar_events():
    # Get events from projects due dates and research schedule
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Project due dates
    c.execute('SELECT id, title, due_date, status FROM projects WHERE due_date IS NOT NULL')
    project_events = [{
        'id': f'project-{row["id"]}',
        'title': row['title'],
        'date': row['due_date'],
        'type': 'project',
        'status': row['status']
    } for row in c.fetchall()]
    
    # Research history
    c.execute('SELECT id, topic, started_at, status FROM research_history')
    research_events = [{
        'id': f'research-{row["id"]}',
        'title': row['topic'],
        'date': row['started_at'],
        'type': 'research',
        'status': row['status']
    } for row in c.fetchall()]
    
    conn.close()
    
    return jsonify({'events': project_events + research_events})

# Memory API
@app.route('/api/memory/search', methods=['GET'])
@login_required
def search_memory():
    query = request.args.get('q', '')
    
    memory_dir = os.path.expanduser('~/.openclaw/workspace/memory')
    results = []
    
    try:
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(memory_dir, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if query.lower() in content.lower():
                        # Find context around match
                        idx = content.lower().find(query.lower())
                        start = max(0, idx - 100)
                        end = min(len(content), idx + 200)
                        snippet = content[start:end]
                        
                        results.append({
                            'filename': filename,
                            'snippet': snippet,
                            'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
                        })
    except Exception as e:
        return jsonify({'error': str(e), 'results': []})
    
    return jsonify({'results': results, 'query': query})

@app.route('/api/memory/file')
@login_required
def get_memory_file():
    filename = request.args.get('file')
    if not filename:
        return jsonify({'error': 'No file specified'}), 400
    
    filename = os.path.basename(filename)
    filepath = os.path.expanduser(f'~/.openclaw/workspace/memory/{filename}')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({'content': content, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# Enhanced Memory Browser API
@app.route('/api/memory/folders', methods=['GET'])
@login_required
def get_memory_folders():
    """Get memory files organized by year/month"""
    memory_dir = os.path.expanduser('~/.openclaw/workspace/memory')
    folders = {}
    
    try:
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(memory_dir, filename)
                stat = os.stat(filepath)
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                # Organize by year-month
                year_month = modified.strftime('%Y-%m')
                year = modified.strftime('%Y')
                month = modified.strftime('%B')
                
                if year not in folders:
                    folders[year] = {}
                
                if year_month not in folders[year]:
                    folders[year][year_month] = {
                        'label': f"{month} {year}",
                        'files': []
                    }
                
                folders[year][year_month]['files'].append({
                    'filename': filename,
                    'title': filename.replace('.md', '').replace('_', ' ').title(),
                    'date': modified.strftime('%Y-%m-%d'),
                    'size': stat.st_size
                })
        
        # Sort files within each month by date (newest first)
        for year in folders:
            for month_key in folders[year]:
                folders[year][month_key]['files'].sort(
                    key=lambda x: x['date'], 
                    reverse=True
                )
        
        return jsonify({'folders': folders})
    except Exception as e:
        return jsonify({'error': str(e), 'folders': {}})

@app.route('/api/memory/files', methods=['GET'])
@login_required
def get_memory_files_list():
    """Get all memory files with metadata"""
    memory_dir = os.path.expanduser('~/.openclaw/workspace/memory')
    files = []
    
    try:
        for filename in os.listdir(memory_dir):
            if filename.endswith('.md'):
                filepath = os.path.join(memory_dir, filename)
                stat = os.stat(filepath)
                modified = datetime.fromtimestamp(stat.st_mtime)
                
                files.append({
                    'filename': filename,
                    'title': filename.replace('.md', '').replace('_', ' ').title(),
                    'date': modified.strftime('%Y-%m-%d'),
                    'datetime': modified.isoformat(),
                    'size': stat.st_size
                })
        
        # Sort by date (newest first)
        files.sort(key=lambda x: x['datetime'], reverse=True)
        
        return jsonify({'files': files})
    except Exception as e:
        return jsonify({'error': str(e), 'files': []})

# Research Folders API
@app.route('/api/research/folders', methods=['GET'])
@login_required
def get_research_folders():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT f.id, f.name, f.description, COUNT(r.id) as file_count
                 FROM research_folders f
                 LEFT JOIN research_files r ON f.id = r.folder_id
                 GROUP BY f.id
                 ORDER BY f.name''')
    
    folders = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'folders': folders})

@app.route('/api/research/folders/<int:folder_id>/files', methods=['GET'])
@login_required
def get_folder_files(folder_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('''SELECT id, filename, title, date, created_at
                 FROM research_files
                 WHERE folder_id = ?
                 ORDER BY date DESC, created_at DESC''', (folder_id,))
    
    files = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'files': files})

@app.route('/api/research/files/<int:file_id>', methods=['GET'])
@login_required
def get_research_file(file_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute('SELECT filename, title FROM research_files WHERE id = ?', (file_id,))
    row = c.fetchone()
    conn.close()
    
    if not row:
        return jsonify({'error': 'File not found'}), 404
    
    filepath = os.path.expanduser(f'~/.openclaw/workspace/memory/research/{row["filename"]}')
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'content': content,
            'filename': row['filename'],
            'title': row['title']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/research/custom', methods=['POST'])
@login_required
def trigger_custom_research():
    data = request.json
    topic = data.get('topic', 'general research')
    
    # Add to research history
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO research_history (topic, status, model_used) VALUES (?, ?, ?)',
              (topic, 'running', 'kimi-coding/k2p5'))
    research_id = c.lastrowid
    conn.commit()
    conn.close()
    
    # Spawn research subagent
    try:
        subprocess.Popen(
            [OPENCLAW_CMD, 'sessions', 'spawn',
             '--task', f'Research: {topic}. Use web_fetch to gather information and save to memory/research/',
             '--model', 'kimi-coding/k2p5',
             '--mode', 'run'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
    
    socketio.emit('research_started', {'id': research_id, 'topic': topic})
    return jsonify({'success': True, 'id': research_id, 'topic': topic})

# Notifications API
@app.route('/api/notifications', methods=['GET'])
@login_required
def get_notifications():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM notifications ORDER BY created_at DESC LIMIT 20')
    notifications = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'notifications': notifications})

@app.route('/api/notifications/<int:note_id>/read', methods=['POST'])
@login_required
def mark_notification_read(note_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE notifications SET read=1 WHERE id=?', (note_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Quick Actions API
@app.route('/api/actions/check-status', methods=['POST'])
@login_required
def action_check_status():
    """Run comprehensive system check"""
    try:
        # Check OpenClaw
        oc_result = subprocess.run([OPENCLAW_CMD, 'status'], capture_output=True, text=True, timeout=10, shell=True)
        oc_ok = oc_result.returncode == 0
        
        # Check Ollama
        ol_result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=5, shell=True)
        ol_ok = ol_result.returncode == 0
        
        # Check disk space
        disk = psutil.disk_usage('/')
        disk_ok = disk.percent < 90
        
        return jsonify({
            'success': True,
            'openclaw': 'running' if oc_ok else 'error',
            'ollama': 'running' if ol_ok else 'error',
            'disk': f"{disk.percent}% used" if disk_ok else f"WARNING: {disk.percent}% used",
            'status': 'healthy' if all([oc_ok, ol_ok, disk_ok]) else 'warning'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/actions/restart-ollama', methods=['POST'])
@login_required
def action_restart_ollama():
    """Restart Ollama service"""
    try:
        # Kill existing ollama processes
        subprocess.run(['taskkill', '/F', '/IM', 'ollama.exe'], capture_output=True, shell=True)
        time.sleep(2)
        
        # Start Ollama
        subprocess.Popen(['ollama', 'serve'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        
        # Add notification
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('INSERT INTO notifications (title, message, type) VALUES (?, ?, ?)',
                  ('Ollama Restarted', 'Ollama service has been restarted successfully', 'success'))
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Ollama restarted'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/actions/github-backup', methods=['POST'])
@login_required
def action_github_backup():
    """Backup to GitHub"""
    try:
        workspace = os.path.expanduser('~/.openclaw/workspace')
        
        # Git add, commit, push
        subprocess.run(['git', 'add', '-A'], cwd=workspace, check=True, shell=True)
        subprocess.run(['git', 'commit', '-m', f'Auto backup - {datetime.now().isoformat()}'], 
                      cwd=workspace, shell=True)
        result = subprocess.run(['git', 'push'], cwd=workspace, capture_output=True, text=True, shell=True)
        
        if result.returncode == 0:
            # Add notification
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute('INSERT INTO notifications (title, message, type) VALUES (?, ?, ?)',
                      ('GitHub Backup', 'Successfully backed up to GitHub', 'success'))
            conn.commit()
            conn.close()
            return jsonify({'success': True, 'message': 'Backed up to GitHub'})
        else:
            return jsonify({'success': False, 'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/actions/clear-logs', methods=['POST'])
@login_required
def action_clear_logs():
    """Clear old log files"""
    try:
        log_dir = os.path.expanduser('~/.openclaw')
        cleared = 0
        
        for filename in os.listdir(log_dir):
            if filename.endswith('.log') and filename != 'openclaw.log':
                filepath = os.path.join(log_dir, filename)
                os.remove(filepath)
                cleared += 1
        
        return jsonify({'success': True, 'message': f'Cleared {cleared} log files'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Notifications API - Enhanced
@app.route('/api/notifications/check', methods=['GET'])
@login_required
def check_notifications():
    """Check for system issues and generate notifications"""
    notifications = []
    
    # Check disk space
    disk = psutil.disk_usage('/')
    if disk.percent > 85:
        notifications.append({
            'title': 'Low Disk Space',
            'message': f'Disk is {disk.percent}% full. Consider cleaning up files.',
            'type': 'warning',
            'timestamp': datetime.now().isoformat()
        })
    
    # Check memory
    memory = psutil.virtual_memory()
    if memory.percent > 90:
        notifications.append({
            'title': 'High Memory Usage',
            'message': f'Memory is {memory.percent}% used. Consider closing applications.',
            'type': 'warning',
            'timestamp': datetime.now().isoformat()
        })
    
    # Check Ollama
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, timeout=5, shell=True)
        if result.returncode != 0:
            notifications.append({
                'title': 'Ollama Not Responding',
                'message': 'Ollama service may be down. Try restarting it.',
                'type': 'error',
                'timestamp': datetime.now().isoformat()
            })
    except:
        notifications.append({
            'title': 'Ollama Check Failed',
            'message': 'Could not check Ollama status.',
            'type': 'warning',
            'timestamp': datetime.now().isoformat()
        })
    
    # Check for recent research completion (within last hour)
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT topic, completed_at FROM research_history 
                 WHERE completed_at > datetime('now', '-1 hour')
                 AND status = 'completed'
                 ORDER BY completed_at DESC LIMIT 3''')
    for row in c.fetchall():
        notifications.append({
            'title': 'Research Complete',
            'message': f'Research on "{row[0]}" has completed.',
            'type': 'success',
            'timestamp': row[1]
        })
    conn.close()
    
    return jsonify({'notifications': notifications})

# Cron Jobs API
@app.route('/api/cron')
@login_required
def api_cron():
    try:
        result = subprocess.run(
            [OPENCLAW_CMD, 'cron', 'list'],
            capture_output=True,
            text=True,
            timeout=10,
            shell=True
        )
        lines = result.stdout.strip().split('\n')
        jobs = []
        for line in lines[1:]:
            if line.strip() and not line.startswith('ID'):
                parts = line.split()
                if len(parts) >= 5:
                    jobs.append({
                        'id': parts[0],
                        'name': parts[1] if len(parts) > 1 else 'unknown',
                        'schedule': ' '.join(parts[2:6]) if len(parts) > 5 else 'unknown',
                        'next': parts[-3] if len(parts) > 3 else 'unknown',
                        'status': parts[-4] if len(parts) > 4 else 'unknown'
                    })
        return jsonify({'jobs': jobs})
    except Exception as e:
        return jsonify({'error': str(e), 'jobs': []})

# Weather API
@app.route('/api/weather', methods=['GET'])
@login_required
def get_weather():
    """Get current weather using wttr.in"""
    try:
        import requests
        
        # Get location from query param or default to Dublin
        location = request.args.get('location', 'Dublin')
        
        # Use wttr.in for weather data
        url = f'https://wttr.in/{location}?format=j1'
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            current = data['current_condition'][0]
            
            return jsonify({
                'success': True,
                'location': location,
                'temp_c': current['temp_C'],
                'temp_f': current['temp_F'],
                'description': current['weatherDesc'][0]['value'],
                'humidity': current['humidity'],
                'wind_speed': current['windspeedKmph'],
                'feels_like_c': current['FeelsLikeC'],
                'feels_like_f': current['FeelsLikeF'],
                'visibility': current['visibility'],
                'pressure': current['pressure'],
                'icon': get_weather_icon(current['weatherDesc'][0]['value'])
            })
        else:
            return jsonify({'success': False, 'error': 'Weather service unavailable'}), 503
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_weather_icon(description):
    """Map weather description to emoji icon"""
    description = description.lower()
    icons = {
        'sunny': '☀️',
        'clear': '🌙',
        'partly cloudy': '⛅',
        'cloudy': '☁️',
        'overcast': '☁️',
        'rain': '🌧️',
        'light rain': '🌦️',
        'heavy rain': '⛈️',
        'snow': '❄️',
        'sleet': '🌨️',
        'thunder': '⚡',
        'fog': '🌫️',
        'mist': '🌫️'
    }
    
    for key, icon in icons.items():
        if key in description:
            return icon
    return '🌡️'

# Pomodoro API
@app.route('/api/pomodoro', methods=['GET'])
@login_required
def get_pomodoro_stats():
    """Get pomodoro statistics"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Get today's completed pomodoros
    c.execute('''SELECT COUNT(*) as count FROM pomodoro_sessions 
                 WHERE completed = 1 AND date(started_at) = date('now')''')
    today_count = c.fetchone()['count']
    
    # Get total completed pomodoros
    c.execute('SELECT COUNT(*) as count FROM pomodoro_sessions WHERE completed = 1')
    total_count = c.fetchone()['count']
    
    # Get pomodoros by project (last 7 days)
    c.execute('''SELECT p.title, COUNT(*) as count 
                 FROM pomodoro_sessions ps
                 JOIN projects p ON ps.project_id = p.id
                 WHERE ps.completed = 1 
                 AND ps.started_at >= datetime('now', '-7 days')
                 GROUP BY p.id
                 ORDER BY count DESC''')
    project_stats = [dict(row) for row in c.fetchall()]
    
    conn.close()
    return jsonify({
        'today': today_count,
        'total': total_count,
        'project_stats': project_stats
    })

@app.route('/api/pomodoro', methods=['POST'])
@login_required
def create_pomodoro():
    """Create a new pomodoro session"""
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO pomodoro_sessions (project_id, duration) VALUES (?, ?)',
              (data.get('project_id'), data.get('duration', 25)))
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return jsonify({'success': True, 'id': session_id})

@app.route('/api/pomodoro/<int:session_id>/complete', methods=['POST'])
@login_required
def complete_pomodoro(session_id):
    """Mark a pomodoro session as completed"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE pomodoro_sessions SET completed = 1, completed_at = CURRENT_TIMESTAMP WHERE id = ?',
              (session_id,))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# Activity Log API
@app.route('/api/activity', methods=['GET'])
@login_required
def get_activity_log():
    """Get recent activity (last 20 items)"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM activity_log ORDER BY created_at DESC LIMIT 20')
    activities = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'activities': activities})

@app.route('/api/activity', methods=['POST'])
@login_required
def add_activity():
    """Add an activity entry"""
    data = request.json
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO activity_log (action, details) VALUES (?, ?)',
              (data.get('action'), data.get('details')))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

# System Uptime API
@app.route('/api/system/uptime', methods=['GET'])
@login_required
def get_system_uptime():
    """Get system uptime and boot time"""
    try:
        import psutil
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return jsonify({
            'boot_time': boot_time.isoformat(),
            'uptime_seconds': uptime.total_seconds(),
            'uptime_formatted': f"{days}d {hours}h {minutes}m",
            'days': days,
            'hours': hours,
            'minutes': minutes
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Project Favorites API
@app.route('/api/projects/<int:project_id>/favorite', methods=['POST'])
@login_required
def toggle_project_favorite(project_id):
    """Toggle favorite status of a project"""
    data = request.json
    favorite = data.get('favorite', False)
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('UPDATE projects SET favorite = ? WHERE id = ?', (favorite, project_id))
    conn.commit()
    conn.close()
    
    # Log activity
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO activity_log (action, details) VALUES (?, ?)',
              ('project_favorite', f'Project {project_id} favorite set to {favorite}'))
    conn.commit()
    conn.close()
    
    socketio.emit('project_updated', {'id': project_id})
    return jsonify({'success': True, 'favorite': favorite})

@app.route('/api/projects/favorites', methods=['GET'])
@login_required
def get_favorite_projects():
    """Get all favorite projects"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM projects WHERE favorite = 1 ORDER BY updated_at DESC')
    projects = [dict(row) for row in c.fetchall()]
    conn.close()
    return jsonify({'projects': projects})

# Data Export/Import
@app.route('/api/export', methods=['GET'])
@login_required
def export_data():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    data = {}
    
    c.execute('SELECT * FROM projects')
    data['projects'] = [dict(row) for row in c.fetchall()]
    
    c.execute('SELECT * FROM research_history')
    data['research_history'] = [dict(row) for row in c.fetchall()]
    
    c.execute('SELECT * FROM notifications')
    data['notifications'] = [dict(row) for row in c.fetchall()]
    
    conn.close()
    
    return jsonify(data)

@app.route('/api/import', methods=['POST'])
@login_required
def import_data():
    data = request.json
    
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    try:
        # Import projects
        for project in data.get('projects', []):
            c.execute('''INSERT INTO projects (title, description, status, priority, due_date, tags, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''',
                      (project.get('title'), project.get('description'), project.get('status'),
                       project.get('priority'), project.get('due_date'), project.get('tags'), project.get('notes')))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'imported_projects': len(data.get('projects', []))})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)}), 500

# Daily Briefing
@app.route('/api/briefing')
@login_required
def get_daily_briefing():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    # Today's tasks
    today = datetime.now().strftime('%Y-%m-%d')
    c.execute('SELECT COUNT(*) as count FROM projects WHERE status="active" AND due_date=?', (today,))
    due_today = c.fetchone()['count']
    
    # Active projects
    c.execute('SELECT COUNT(*) as count FROM projects WHERE status="active"')
    active_projects = c.fetchone()['count']
    
    # Recent research
    c.execute('SELECT COUNT(*) as count FROM research_history WHERE date(started_at)=date("now")')
    research_today = c.fetchone()['count']
    
    # System status
    system = get_system_data()
    
    conn.close()
    
    return jsonify({
        'date': today,
        'due_today': due_today,
        'active_projects': active_projects,
        'research_today': research_today,
        'system_status': 'healthy' if system['memory']['percent'] < 80 else 'warning',
        'greeting': f"Good {('morning' if datetime.now().hour < 12 else 'afternoon' if datetime.now().hour < 18 else 'evening')}, Ken!"
    })

# Models API
@app.route('/api/models')
@login_required
def api_models():
    return jsonify({
        'local': [
            {'id': 'ollama/qwen2.5:7b', 'name': 'Qwen 2.5 7B', 'type': 'local'},
            {'id': 'ollama/qwen2.5:14b', 'name': 'Qwen 2.5 14B', 'type': 'local'},
            {'id': 'ollama/nomic-embed-text', 'name': 'Nomic Embed', 'type': 'embedding'}
        ],
        'cloud': [
            {'id': 'kimi-coding/k2p5', 'name': 'Kimi K2.5', 'type': 'cloud', 'default': True}
        ]
    })

if __name__ == '__main__':
    print('Karen Dashboard starting...')
    print('Local: http://localhost:5000')
    print('Network: http://100.75.72.26:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)
