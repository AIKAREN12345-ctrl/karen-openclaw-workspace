from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import json
import os
import subprocess
import glob
from datetime import datetime
import threading
import time

app = Flask(__name__)
CORS(app)

# Paths
DASHBOARD_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(DASHBOARD_DIR)
MEMORY_DIR = os.path.join(WORKSPACE_DIR, 'memory')
RESEARCH_DIR = os.path.join(MEMORY_DIR, 'research')

# Cache for system stats
system_cache = {
    "last_update": None,
    "openclaw_version": "2026.3.2",
    "gateway_status": "✅ Online",
    "memory_files": 171,
    "memory_chunks": 1144,
    "sessions": 36,
    "ollama_models": ["nomic-embed-text", "qwen3.5:9b", "qwen2.5:14b"],
    "ollama_running": "⚪ Idle",
    "disk_used": "176 GB",
    "disk_free": "754 GB"
}

def update_system_stats():
    """Background thread to update system stats every 30 seconds"""
    while True:
        try:
            # OpenClaw status
            try:
                result = subprocess.run(['openclaw', 'status'], capture_output=True, text=True, timeout=15)
                output = result.stdout
                if 'reachable' in output.lower():
                    system_cache["gateway_status"] = "✅ Online"
                elif 'error' in output.lower():
                    system_cache["gateway_status"] = "❌ Error"
                else:
                    system_cache["gateway_status"] = "⚠️ Check"
            except:
                pass
            
            # Ollama running
            try:
                result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=10)
                lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('NAME')]
                if lines:
                    system_cache["ollama_running"] = "🟢 Running"
                else:
                    system_cache["ollama_running"] = "⚪ Idle"
            except:
                pass
            
            system_cache["last_update"] = datetime.now().isoformat()
            
        except Exception as e:
            print(f"Stats update error: {e}")
        
        time.sleep(30)

# Start background updater
stats_thread = threading.Thread(target=update_system_stats, daemon=True)
stats_thread.start()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Karen Dashboard v3</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #0a0a0f;
            color: #e0e0e0;
            min-height: 100vh;
            display: flex;
        }
        
        /* Sidebar */
        .sidebar {
            width: 160px;
            background: #151520;
            border-right: 1px solid #2a2a3a;
            display: flex;
            flex-direction: column;
            position: fixed;
            height: 100vh;
            left: 0;
            top: 0;
            z-index: 100;
            transform: translateX(-100%);
            transition: transform 0.3s ease;
        }
        
        .sidebar.visible {
            transform: translateX(0);
        }
        
        /* Menu Toggle Button */
        .menu-toggle {
            display: block;
            position: fixed;
            top: 10px;
            left: 10px;
            z-index: 200;
            background: #151520;
            border: 1px solid #2a2a3a;
            color: #e0e0e0;
            padding: 8px 12px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1.2em;
        }
        
        .menu-toggle:hover {
            background: #1a1a25;
        }
        
        /* Overlay */
        .sidebar-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.5);
            z-index: 99;
        }
        
        .sidebar-overlay.active {
            display: block;
        }
        
        .sidebar-header {
            padding: 15px 10px;
            border-bottom: 1px solid #2a2a3a;
            text-align: center;
        }
        
        .sidebar-header h1 {
            font-size: 1.1em;
            background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        .sidebar-header p {
            color: #666;
            font-size: 0.7em;
            margin-top: 5px;
        }
        
        .tailscale-box {
            background: #1a1a25;
            padding: 8px;
            border-radius: 4px;
            margin-top: 10px;
            font-family: monospace;
            font-size: 0.7em;
            color: #4ecdc4;
            word-break: break-all;
        }
        
        .nav-menu {
            flex: 1;
            padding: 10px 0;
        }
        
        .nav-item {
            display: block;
            padding: 12px 15px;
            text-decoration: none;
            color: #e0e0e0;
            border-left: 3px solid transparent;
            transition: all 0.2s;
        }
        
        .nav-item:hover {
            background: #1a1a25;
        }
        
        .nav-item.active {
            background: #1a1a25;
            border-left-color: #4ecdc4;
        }
        
        .nav-item .icon {
            font-size: 1.1em;
            margin-right: 8px;
        }
        
        .sidebar-footer {
            padding: 15px;
            border-top: 1px solid #2a2a3a;
            font-size: 0.7em;
            color: #666;
            text-align: center;
        }
        
        /* Main Content */
        .main-content {
            flex: 1;
            margin-left: 0;
            padding: 50px 15px 15px 15px;
            min-height: 100vh;
        }
        
        .page-header {
            margin-bottom: 20px;
        }
        
        .page-header h2 {
            font-size: 1.4em;
            margin-bottom: 5px;
        }
        
        .page-header p {
            color: #888;
            font-size: 0.9em;
        }
        
        /* Cards */
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }
        
        .card {
            background: #151520;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #2a2a3a;
        }
        
        .card h3 {
            font-size: 1.1em;
            margin-bottom: 15px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            padding: 12px 0;
            border-bottom: 1px solid #2a2a3a;
            gap: 10px;
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-label {
            color: #888;
            font-size: 0.9em;
        }
        
        .metric-value {
            font-weight: 500;
            font-family: monospace;
            text-align: right;
            word-break: break-word;
            max-width: 65%;
        }
        
        .status-online { color: #22c55e; }
        
        /* Sub-nav */
        .sub-nav {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .sub-nav-item {
            display: inline-block;
            padding: 10px 20px;
            border-radius: 8px;
            text-decoration: none;
            color: #e0e0e0;
            background: #1a1a25;
            border: 1px solid #2a2a3a;
            transition: all 0.2s;
        }
        
        .sub-nav-item:hover {
            background: #252535;
        }
        
        .sub-nav-item.active {
            background: #ff6b6b;
            color: #0a0a0f;
            border-color: #ff6b6b;
        }
        
        /* File lists */
        .file-list {
            max-height: 500px;
            overflow-y: auto;
        }
        
        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px;
            background: #1a1a25;
            border-radius: 6px;
            margin-bottom: 8px;
            cursor: pointer;
            transition: background 0.2s;
        }
        
        .file-item:hover {
            background: #252535;
        }
        
        .file-name {
            font-family: monospace;
            font-size: 0.85em;
        }
        
        .file-date {
            color: #666;
            font-size: 0.75em;
        }
        
        /* Tasks */
        .task-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 14px;
            background: #1a1a25;
            border-radius: 8px;
            margin-bottom: 10px;
        }
        
        .task-checkbox {
            width: 20px;
            height: 20px;
            cursor: pointer;
        }
        
        .task-text {
            flex: 1;
            font-size: 0.95em;
        }
        
        .task-priority {
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.7em;
            text-transform: uppercase;
            font-weight: 600;
        }
        
        .priority-high { background: #ef444420; color: #ef4444; }
        .priority-medium { background: #f59e0b20; color: #f59e0b; }
        .priority-low { background: #22c55e20; color: #22c55e; }
        
        .btn {
            padding: 10px 20px;
            border-radius: 8px;
            border: none;
            cursor: pointer;
            font-size: 0.95em;
            background: #4ecdc4;
            color: #0a0a0f;
            font-weight: 500;
        }
        
        /* Modal */
        .modal-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 1000;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .modal-overlay.active {
            display: flex;
        }
        
        .modal {
            background: #151520;
            border-radius: 12px;
            width: 90%;
            max-width: 800px;
            max-height: 80vh;
            display: flex;
            flex-direction: column;
            border: 1px solid #2a2a3a;
        }
        
        .modal-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 20px;
            border-bottom: 1px solid #2a2a3a;
        }
        
        .modal-header h3 {
            margin: 0;
            font-size: 1.1em;
        }
        
        .modal-close {
            background: none;
            border: none;
            color: #888;
            font-size: 1.5em;
            cursor: pointer;
            padding: 0 5px;
        }
        
        .modal-close:hover {
            color: #fff;
        }
        
        .modal-body {
            padding: 20px;
            overflow-y: auto;
            max-height: 60vh;
        }
        
        .modal-content {
            white-space: pre-wrap;
            font-family: monospace;
            font-size: 0.85em;
            line-height: 1.6;
            color: #e0e0e0;
        }
        
        .refresh-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #22c55e;
            margin-left: 8px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
    </style>
</head>
<body>
    <!-- Menu Toggle Button -->
    <button class="menu-toggle" onclick="toggleSidebar()">☰</button>
    
    <!-- Sidebar Overlay -->
    <div class="sidebar-overlay" onclick="toggleSidebar()"></div>
    
    <!-- Sidebar -->
    <div class="sidebar" id="sidebar">
        <div class="sidebar-header">
            <h1>Karen</h1>
            <p>Dashboard</p>
            <div class="tailscale-box">100.75.72.26:5000</div>
        </div>
        
        <div class="nav-menu">
            <a href="/" class="nav-item {{ 'active' if page == 'system' else '' }}">
                <span class="icon">🖥️</span>System
            </a>
            <a href="/memory" class="nav-item {{ 'active' if page == 'memory' else '' }}">
                <span class="icon">🧠</span>Memory
            </a>
            <a href="/tasks" class="nav-item {{ 'active' if page == 'tasks' else '' }}">
                <span class="icon">📝</span>Tasks
            </a>
        </div>
        
        <div class="sidebar-footer">
            Auto-refresh: 30s <span class="refresh-indicator"></span>
        </div>
    </div>
    
    <!-- Main Content -->
    <div class="main-content">
        {{ content | safe }}
    </div>
    
    <!-- Modal -->
    <div class="modal-overlay" id="fileModal">
        <div class="modal">
            <div class="modal-header">
                <h3 id="modalTitle">File Viewer</h3>
                <button class="modal-close" onclick="closeModal()">×</button>
            </div>
            <div class="modal-body">
                <pre class="modal-content" id="modalContent">Loading...</pre>
            </div>
        </div>
    </div>
    
    <script>
        // Modal functions
        function openModal(title, content) {
            document.getElementById('modalTitle').textContent = title;
            document.getElementById('modalContent').textContent = content;
            document.getElementById('fileModal').classList.add('active');
        }
        
        function closeModal() {
            document.getElementById('fileModal').classList.remove('active');
        }
        
        // Close modal when clicking overlay
        document.getElementById('fileModal').addEventListener('click', function(e) {
            if (e.target === this) {
                closeModal();
            }
        });
        
        // Load and view file
        async function viewFile(type, filename) {
            try {
                const response = await fetch(`/api/file/${type}/${encodeURIComponent(filename)}`);
                const data = await response.json();
                if (data.content) {
                    openModal(filename, data.content);
                } else {
                    openModal('Error', 'Failed to load file');
                }
            } catch (e) {
                openModal('Error', 'Failed to load file: ' + e.message);
            }
        }
        
        // Sidebar toggle for mobile
        function toggleSidebar() {
            const sidebar = document.getElementById('sidebar');
            const overlay = document.querySelector('.sidebar-overlay');
            sidebar.classList.toggle('visible');
            overlay.classList.toggle('active');
        }
        
        // Close sidebar when clicking a nav item on mobile
        document.querySelectorAll('.nav-item').forEach(item => {
            item.addEventListener('click', () => {
                if (window.innerWidth <= 768) {
                    toggleSidebar();
                }
            });
        });
        // Auto-refresh stats every 30 seconds
        setInterval(async function() {
            try {
                const response = await fetch('/api/stats');
                const data = await response.json();
                
                // Update all elements with data attributes
                document.querySelectorAll('[data-stat]').forEach(el => {
                    const stat = el.getAttribute('data-stat');
                    if (data[stat]) {
                        el.textContent = data[stat];
                    }
                });
            } catch (e) {
                console.error('Failed to refresh stats:', e);
            }
        }, 30000);
    </script>
</body>
</html>
'''

SYSTEM_PAGE = '''
<div class="page-header">
    <h2>🖥️ System Status</h2>
    <p>Karen's PC and Ollama monitoring</p>
</div>

<div class="grid">
    <div class="card">
        <h3>💻 Karen's PC</h3>
        <div class="metric">
            <span class="metric-label">Hostname</span>
            <span class="metric-value" id="pc-hostname">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">OS</span>
            <span class="metric-value" id="pc-os">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">CPU</span>
            <span class="metric-value" id="pc-cpu">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">RAM Total</span>
            <span class="metric-value" id="pc-ram">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">RAM Used</span>
            <span class="metric-value" id="pc-ram-used">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Disk Used</span>
            <span class="metric-value" id="pc-disk-used">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Disk Free</span>
            <span class="metric-value" id="pc-disk-free">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Uptime</span>
            <span class="metric-value" id="pc-uptime">Loading...</span>
        </div>
    </div>
    
    <div class="card">
        <h3>🦞 OpenClaw</h3>
        <div class="metric">
            <span class="metric-label">Version</span>
            <span class="metric-value" id="oc-version">Loading...</span>
        </div>
    </div>
    
    <div class="card">
        <h3>🤖 Ollama</h3>
        <div class="metric">
            <span class="metric-label">Status</span>
            <span class="metric-value" id="ollama-status">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Loaded Model</span>
            <span class="metric-value" id="ollama-loaded">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Available Models</span>
            <span class="metric-value" id="model-count">Loading...</span>
        </div>
        <div id="ollama-models-list" style="margin-top: 10px;">
            <div class="model-tag">Loading...</div>
        </div>
    </div>
</div>

<style>
.model-tag {
    display: inline-block;
    padding: 4px 10px;
    background: #1a1a25;
    border-radius: 4px;
    font-size: 0.75em;
    margin: 2px;
    border: 1px solid #2a2a3a;
    word-break: break-all;
    max-width: 100%;
}
.model-tag.loaded {
    background: #22c55e20;
    border-color: #22c55e;
    color: #22c55e;
}

#ollama-models-list {
    margin-top: 10px;
    display: flex;
    flex-wrap: wrap;
    gap: 4px;
}
</style>

<script>
// Update all system stats
async function updateSystemStats() {
    try {
        const response = await fetch('/api/system/stats');
        const data = await response.json();
        
        // PC stats
        document.getElementById('pc-hostname').textContent = data.pc_hostname || 'Unknown';
        document.getElementById('pc-os').textContent = data.pc_os || 'Unknown';
        document.getElementById('pc-cpu').textContent = data.pc_cpu || 'Unknown';
        document.getElementById('pc-ram').textContent = data.pc_ram || 'Unknown';
        document.getElementById('pc-ram-used').textContent = data.pc_ram_used || 'Unknown';
        document.getElementById('pc-disk-used').textContent = data.pc_disk_used || 'Unknown';
        document.getElementById('pc-disk-free').textContent = data.pc_disk_free || 'Unknown';
        document.getElementById('pc-uptime').textContent = data.pc_uptime || 'Unknown';
        
        // OpenClaw version
        document.getElementById('oc-version').textContent = data.openclaw_version || 'Unknown';
        
        // Ollama stats
        document.getElementById('ollama-status').textContent = data.ollama_running || 'Unknown';
        document.getElementById('ollama-loaded').textContent = data.ollama_loaded || 'None';
        document.getElementById('model-count').textContent = (data.ollama_models || []).length + ' models';
        
        // Update models list
        const modelsList = document.getElementById('ollama-models-list');
        if (data.ollama_models && data.ollama_models.length > 0) {
            modelsList.innerHTML = data.ollama_models.map(m => 
                `\u003cdiv class="model-tag ${m.loaded ? 'loaded' : ''}">${m.name}${m.loaded ? ' ●' : ''}\u003c/div>`
            ).join('');
        } else {
            modelsList.innerHTML = '\u003cdiv class="model-tag">No models</div>';
        }
        
        // Update refresh time
        document.getElementById('last-refresh-time').textContent = new Date().toLocaleTimeString();
    } catch (e) {
        console.error('Failed to update system stats:', e);
    }
}

// Initial load and auto-refresh
updateSystemStats();
setInterval(updateSystemStats, 30000);
</script>
'''

MEMORY_PAGE = '''
<div class="page-header">
    <h2>🧠 Memory System</h2>
    <p>Memory stats and file browser</p>
</div>

<div class="grid">
    <div class="card">
        <h3>🧠 Stats</h3>
        <div class="metric">
            <span class="metric-label">Memory Files</span>
            <span class="metric-value" id="mem-files-count">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Research Files</span>
            <span class="metric-value" id="research-files-count">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Chunks</span>
            <span class="metric-value" id="mem-chunks-count">Loading...</span>
        </div>
        <div class="metric">
            <span class="metric-label">Vector Search</span>
            <span class="metric-value status-online">✅ Ready</span>
        </div>
        <div class="metric">
            <span class="metric-label">FTS Search</span>
            <span class="metric-value status-online">✅ Ready</span>
        </div>
    </div>
</div>

<div class="sub-nav">
    <a href="/memory" class="sub-nav-item {{ 'active' if subpage == 'files' else '' }}">📁 Memory Files</a>
    <a href="/memory/research" class="sub-nav-item {{ 'active' if subpage == 'research' else '' }}">🔬 Research Files</a>
</div>

{{ files_content | safe }}

<script>
// Update memory stats
async function updateMemoryStats() {
    try {
        const response = await fetch('/api/memory/stats');
        const data = await response.json();
        
        document.getElementById('mem-files-count').textContent = data.files || '0';
        document.getElementById('research-files-count').textContent = data.research_files || '0';
        document.getElementById('mem-chunks-count').textContent = data.chunks || '0';
    } catch (e) {
        console.error('Failed to update memory stats:', e);
    }
}

// Initial load
updateMemoryStats();
setInterval(updateMemoryStats, 30000);
</script>
'''

TASKS_PAGE = '''
<div class="page-header">
    <h2>📝 Tasks</h2>
    <p>Task tracker and management</p>
</div>

<div class="card">
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
        <h3>Active Tasks</h3>
        <button class="btn" onclick="addTask()">+ Add Task</button>
    </div>
    
    <div id="tasks-list">
        <p>Loading tasks...</p>
    </div>
</div>

<script>
// Load tasks from server
async function loadTasks() {
    try {
        const response = await fetch('/api/tasks');
        const tasks = await response.json();
        
        const container = document.getElementById('tasks-list');
        if (tasks.length === 0) {
            container.innerHTML = '\u003cp\u003eNo tasks yet. Add one above!\u003c/p\u003e';
            return;
        }
        
        container.innerHTML = tasks.map(t => `
            \u003cdiv class="task-item" data-id="${t.id}">
                \u003cinput type="checkbox" class="task-checkbox" ${t.done ? 'checked' : ''} onchange="toggleTask('${t.id}')">
                \u003cspan class="task-text" style="${t.done ? 'text-decoration: line-through; opacity: 0.6;' : ''}">${t.text}\u003c/span>
                \u003cspan class="task-priority priority-${t.priority}">${t.priority}\u003c/span>
            \u003c/div>
        `).join('');
    } catch (e) {
        document.getElementById('tasks-list').innerHTML = '\u003cp\u003eError loading tasks\u003c/p\u003e';
    }
}

// Add new task
async function addTask() {
    const text = prompt('Task description:');
    if (!text) return;
    
    const priority = prompt('Priority: (high/medium/low)', 'medium');
    
    try {
        await fetch('/api/tasks', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({text, priority})
        });
        loadTasks();
    } catch (e) {
        alert('Failed to add task');
    }
}

// Toggle task done status
async function toggleTask(id) {
    // For now just visual, could sync to server
    const item = document.querySelector(`[data-id="${id}"]`);
    const text = item.querySelector('.task-text');
    const checkbox = item.querySelector('.task-checkbox');
    
    if (checkbox.checked) {
        text.style.textDecoration = 'line-through';
        text.style.opacity = '0.6';
    } else {
        text.style.textDecoration = 'none';
        text.style.opacity = '1';
    }
}

// Initial load
loadTasks();
</script>
'''

@app.route('/')
def dashboard_system():
    return render_template_string(HTML_TEMPLATE, page='system', content=SYSTEM_PAGE)

@app.route('/memory')
def dashboard_memory():
    # Load memory files
    files_html = load_memory_files_html()
    content = MEMORY_PAGE.replace('{{ files_content | safe }}', files_html)
    return render_template_string(HTML_TEMPLATE, page='memory', subpage='files', content=content)

@app.route('/memory/research')
def dashboard_memory_research():
    # Load research files
    files_html = load_research_files_html()
    content = MEMORY_PAGE.replace('{{ files_content | safe }}', files_html)
    return render_template_string(HTML_TEMPLATE, page='memory', subpage='research', content=content)



@app.route('/tasks')
def dashboard_tasks():
    return render_template_string(HTML_TEMPLATE, page='tasks', content=TASKS_PAGE)

def load_memory_files_html():
    files = []
    if os.path.exists(MEMORY_DIR):
        for f in sorted(glob.glob(os.path.join(MEMORY_DIR, '*.md')), 
                       key=os.path.getmtime, reverse=True)[:50]:
            files.append({
                "name": os.path.basename(f),
                "date": datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d')
            })
    
    if not files:
        return '<div class="card"><p>No memory files found</p></div>'
    
    html = '<div class="card"><h3>📁 Memory Files</h3><div class="file-list">'
    for f in files:
        html += f'<div class="file-item" onclick="viewFile(\'memory\', \'{f["name"]}\')"><span class="file-name">{f["name"]}</span><span class="file-date">{f["date"]}</span></div>'
    html += '</div></div>'
    return html

def load_research_files_html():
    files = []
    if os.path.exists(RESEARCH_DIR):
        for f in sorted(glob.glob(os.path.join(RESEARCH_DIR, '*.md')), 
                       key=os.path.getmtime, reverse=True)[:50]:
            files.append({
                "name": os.path.basename(f),
                "date": datetime.fromtimestamp(os.path.getmtime(f)).strftime('%Y-%m-%d')
            })
    
    if not files:
        return '<div class="card"><p>No research files found</p></div>'
    
    html = '<div class="card"><h3>🔬 Research Files</h3><div class="file-list">'
    for f in files:
        html += f'<div class="file-item" onclick="viewFile(\'research\', \'{f["name"]}\')"><span class="file-name">{f["name"]}</span><span class="file-date">{f["date"]}</span></div>'
    html += '</div></div>'
    return html

@app.route('/api/stats')
def get_stats():
    return jsonify(system_cache)

@app.route('/api/file/memory/<path:filename>')
def get_memory_file(filename):
    filepath = os.path.join(MEMORY_DIR, filename)
    if os.path.exists(filepath) and filepath.startswith(MEMORY_DIR):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return jsonify({"content": f.read()})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File not found"}), 404

@app.route('/api/file/research/<path:filename>')
def get_research_file(filename):
    filepath = os.path.join(RESEARCH_DIR, filename)
    if os.path.exists(filepath) and filepath.startswith(RESEARCH_DIR):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return jsonify({"content": f.read()})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    return jsonify({"error": "File not found"}), 404

@app.route('/api/ollama/status')
def get_ollama_status():
    """Get Ollama status including loaded model and available models"""
    try:
        # Get list of models
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
        models = []
        for line in result.stdout.split('\n')[1:]:  # Skip header
            if line.strip():
                parts = line.split()
                if parts:
                    models.append({"name": parts[0], "loaded": False})
        
        # Get currently running model
        result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=10)
        loaded_model = None
        lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('NAME')]
        if lines:
            parts = lines[0].split()
            if parts:
                loaded_model = parts[0]
                # Mark as loaded in models list
                for m in models:
                    if m["name"] == loaded_model:
                        m["loaded"] = True
        
        return jsonify({
            "loaded": loaded_model or "None",
            "models": models,
            "running": len(lines) > 0
        })
    except Exception as e:
        return jsonify({"error": str(e), "loaded": "Unknown", "models": []}), 500

@app.route('/api/system/stats')
def get_system_stats():
    """Get all system stats dynamically"""
    try:
        # Get OpenClaw version
        version = "2026.3.2"
        try:
            result = subprocess.run(['openclaw', '--version'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                version = result.stdout.strip()
        except:
            pass
        
        # Get Ollama status
        ollama_running = "⚪ Idle"
        ollama_loaded = "None"
        ollama_models = []
        
        try:
            # Get running model
            result = subprocess.run(['ollama', 'ps'], capture_output=True, text=True, timeout=10)
            lines = [l for l in result.stdout.split('\n') if l.strip() and not l.startswith('NAME')]
            if lines:
                ollama_running = "🟢 Running"
                parts = lines[0].split()
                if parts:
                    ollama_loaded = parts[0]
            
            # Get all models
            result = subprocess.run(['ollama', 'list'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n')[1:]:
                if line.strip():
                    parts = line.split()
                    if parts:
                        model_name = parts[0]
                        ollama_models.append({
                            "name": model_name,
                            "loaded": model_name == ollama_loaded
                        })
        except:
            pass
        
        # Get PC stats
        pc_stats = {
            "hostname": "Unknown",
            "os": "Unknown",
            "cpu": "Unknown",
            "ram": "Unknown",
            "ram_used": "Unknown",
            "disk_used": "Unknown",
            "disk_free": "Unknown",
            "uptime": "Unknown"
        }
        
        try:
            # Hostname
            result = subprocess.run(['hostname'], capture_output=True, text=True, timeout=5)
            pc_stats["hostname"] = result.stdout.strip()
        except:
            pass
        
        try:
            # OS info using PowerShell
            result = subprocess.run(['powershell', '-Command', '(Get-CimInstance Win32_OperatingSystem).Caption'], capture_output=True, text=True, timeout=10)
            pc_stats["os"] = result.stdout.strip()
        except:
            pass
        
        try:
            # Total RAM using PowerShell
            result = subprocess.run(['powershell', '-Command', '[math]::Round((Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB, 0)'], capture_output=True, text=True, timeout=10)
            ram_gb = result.stdout.strip()
            if ram_gb:
                pc_stats["ram"] = f"{ram_gb} GB"
        except:
            pass
        
        try:
            # RAM Used using PowerShell (Total - Available)
            result = subprocess.run(['powershell', '-Command', '$total = (Get-CimInstance Win32_PhysicalMemory | Measure-Object -Property Capacity -Sum).Sum / 1GB; $avail = (Get-CimInstance Win32_OperatingSystem).FreePhysicalMemory / 1MB; [math]::Round($total - $avail, 0)'], capture_output=True, text=True, timeout=10)
            ram_used = result.stdout.strip()
            if ram_used:
                pc_stats["ram_used"] = f"{ram_used} GB"
        except:
            pass
        
        try:
            # CPU using PowerShell
            result = subprocess.run(['powershell', '-Command', '(Get-CimInstance Win32_Processor).Name'], capture_output=True, text=True, timeout=10)
            cpu = result.stdout.strip()
            if cpu:
                # Truncate long CPU names
                if len(cpu) > 40:
                    cpu = cpu[:37] + "..."
                pc_stats["cpu"] = cpu
        except:
            pass
        
        try:
            # Disk space using PowerShell
            result = subprocess.run(['powershell', '-Command', '$disk = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID=\'C:\'"; [math]::Round($disk.Size / 1GB, 1), [math]::Round($disk.FreeSpace / 1GB, 1)'], capture_output=True, text=True, timeout=10)
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                total_gb = float(lines[0].strip())
                free_gb = float(lines[1].strip())
                used_gb = total_gb - free_gb
                pc_stats["disk_free"] = f"{free_gb:.1f} GB"
                pc_stats["disk_used"] = f"{used_gb:.1f} GB"
        except:
            pass
        
        try:
            # Uptime using PowerShell
            result = subprocess.run(['powershell', '-Command', '(Get-Date) - (Get-CimInstance Win32_OperatingSystem).LastBootUpTime | Select-Object -ExpandProperty Days'], capture_output=True, text=True, timeout=10)
            days = result.stdout.strip()
            if days:
                pc_stats["uptime"] = f"{days} days"
        except:
            pass
        
        return jsonify({
            "openclaw_version": version,
            "pc_hostname": pc_stats["hostname"],
            "pc_os": pc_stats["os"],
            "pc_cpu": pc_stats["cpu"],
            "pc_ram": pc_stats["ram"],
            "pc_ram_used": pc_stats["ram_used"],
            "pc_disk_used": pc_stats["disk_used"],
            "pc_disk_free": pc_stats["disk_free"],
            "pc_uptime": pc_stats["uptime"],
            "ollama_running": ollama_running,
            "ollama_loaded": ollama_loaded,
            "ollama_models": ollama_models
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/memory/stats')
def get_memory_stats():
    """Get memory stats dynamically"""
    try:
        # Count memory files
        file_count = 0
        if os.path.exists(MEMORY_DIR):
            file_count = len([f for f in os.listdir(MEMORY_DIR) if f.endswith('.md')])
        
        # Count research files
        research_count = 0
        if os.path.exists(RESEARCH_DIR):
            research_count = len([f for f in os.listdir(RESEARCH_DIR) if f.endswith('.md')])
        
        # Try to get chunks from OpenClaw status
        chunks = 0
        try:
            result = subprocess.run(['openclaw', 'status'], capture_output=True, text=True, timeout=10)
            for line in result.stdout.split('\n'):
                if 'chunks' in line:
                    try:
                        parts = line.split('·')
                        for part in parts:
                            if 'chunks' in part:
                                chunks = int(part.split()[0].strip())
                    except:
                        pass
        except:
            pass
        
        # Fallback chunk estimate
        if chunks == 0:
            chunks = file_count * 6  # Rough estimate
        
        return jsonify({
            "files": file_count,
            "research_files": research_count,
            "chunks": chunks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Task storage
TASKS_FILE = os.path.join(DASHBOARD_DIR, 'tasks.json')

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r') as f:
            return json.load(f)
    return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w') as f:
        json.dump(tasks, f, indent=2)

@app.route('/api/tasks')
def get_tasks():
    return jsonify(load_tasks())

@app.route('/api/tasks', methods=['POST'])
def add_task():
    data = request.json
    tasks = load_tasks()
    task = {
        "id": str(int(time.time() * 1000)),
        "text": data.get('text', ''),
        "priority": data.get('priority', 'medium'),
        "done": False,
        "created": datetime.now().isoformat()
    }
    tasks.append(task)
    save_tasks(tasks)
    return jsonify({"status": "ok", "task": task})

@app.route('/api/tasks/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    tasks = load_tasks()
    tasks = [t for t in tasks if t['id'] != task_id]
    save_tasks(tasks)
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting Karen Dashboard")
    print("Local:   http://localhost:5000")
    print("Network: http://192.168.1.130:5000")
    print("Tailscale: http://100.75.72.26:5000")
    print()
    app.run(host='0.0.0.0', port=5000, debug=False)