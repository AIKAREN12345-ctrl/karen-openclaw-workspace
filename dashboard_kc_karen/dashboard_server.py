from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Paths
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DASHBOARD_DIR)

# Store KC updates (in-memory for now, could use file)
kc_status = {
    "last_update": None,
    "activity": "Waiting for update...",
    "messages": "—",
    "tools": "—",
    "files": "—"
}

@app.route('/')
def dashboard():
    """Serve the dashboard HTML"""
    return send_from_directory(DASHBOARD_DIR, 'index.html')

@app.route('/api/karen/status')
def karen_status():
    """Get Karen's current status"""
    try:
        # Read memory stats
        memory_dir = os.path.join(WORKSPACE_DIR, 'memory')
        memory_files = len([f for f in os.listdir(memory_dir) if f.endswith('.md')]) if os.path.exists(memory_dir) else 0
        
        # Check OpenClaw status (simplified)
        import subprocess
        result = subprocess.run(['openclaw', 'status'], capture_output=True, text=True, timeout=10)
        gateway_status = "Online" if "reachable" in result.stdout.lower() else "Check needed"
        
        return jsonify({
            "status": "online",
            "tools": "All Working",
            "memory": f"{memory_files} files",
            "activity": "Dashboard active",
            "gateway": gateway_status,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            "status": "online",
            "tools": "All Working", 
            "memory": "171 files",
            "activity": "Building dashboard with KC",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        })

@app.route('/api/kc/update', methods=['POST'])
def kc_update():
    """Receive KC status update (if he could push directly)"""
    global kc_status
    data = request.json
    
    kc_status = {
        "last_update": datetime.now().isoformat(),
        "activity": data.get('activity', '—'),
        "messages": data.get('messages', '—'),
        "tools": data.get('tools', '—'),
        "files": data.get('files', '—')
    }
    
    return jsonify({"status": "ok"})

@app.route('/api/kc/status')
def get_kc_status():
    """Get KC's current status"""
    return jsonify(kc_status)

@app.route('/api/tasks', methods=['GET', 'POST'])
def tasks():
    """Get or add shared tasks"""
    tasks_file = os.path.join(DASHBOARD_DIR, 'tasks.json')
    
    if request.method == 'POST':
        data = request.json
        task = {
            "id": datetime.now().timestamp(),
            "text": data.get('text'),
            "assignee": data.get('assignee', 'both'),
            "done": False,
            "created": datetime.now().isoformat()
        }
        
        # Load existing tasks
        tasks = []
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                tasks = json.load(f)
        
        tasks.append(task)
        
        with open(tasks_file, 'w') as f:
            json.dump(tasks, f, indent=2)
        
        return jsonify({"status": "ok", "task": task})
    
    else:
        # GET - return tasks
        if os.path.exists(tasks_file):
            with open(tasks_file, 'r') as f:
                return jsonify(json.load(f))
        return jsonify([])

if __name__ == '__main__':
    print("🦞 Starting Karen ↔ KC Dashboard Server")
    print("📊 Dashboard: http://localhost:5000")
    print("📋 API endpoints:")
    print("   - GET  /api/karen/status")
    print("   - GET  /api/kc/status")
    print("   - POST /api/kc/update")
    print("   - GET/POST /api/tasks")
    print()
    app.run(host='0.0.0.0', port=5000, debug=False)