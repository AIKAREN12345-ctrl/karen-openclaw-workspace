from flask import Flask, render_template, jsonify, request
import psutil
import os
from datetime import datetime
import requests

app = Flask(__name__)

# Simple in-memory "database"
projects = []
notes = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/system')
def system_info():
    cpu = psutil.cpu_percent(interval=0.1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    return jsonify({
        'cpu': cpu,
        'memory': {'percent': mem.percent, 'used': round(mem.used/1024**3, 1), 'total': round(mem.total/1024**3, 1)},
        'disk': {'percent': round(disk.percent, 1), 'free': round(disk.free/1024**3, 1)},
        'time': datetime.now().strftime('%H:%M:%S')
    })

@app.route('/api/projects', methods=['GET', 'POST'])
def handle_projects():
    global projects
    if request.method == 'POST':
        data = request.get_json()
        projects.append({
            'id': len(projects) + 1,
            'title': data.get('title', ''),
            'status': data.get('status', 'todo'),
            'created': datetime.now().isoformat()
        })
        return jsonify({'success': True})
    return jsonify({'projects': projects})

@app.route('/api/notes', methods=['GET', 'POST'])
def handle_notes():
    global notes
    if request.method == 'POST':
        data = request.get_json()
        notes.append({
            'id': len(notes) + 1,
            'text': data.get('text', ''),
            'time': datetime.now().isoformat()
        })
        return jsonify({'success': True})
    return jsonify({'notes': notes[-10:]})  # Last 10 only

@app.route('/api/chat', methods=['POST'])
def chat():
    data = request.get_json()
    message = data.get('message', '')
    model = data.get('model', 'qwen2.5:7b')
    
    try:
        response = requests.post('http://localhost:11434/api/generate', json={
            'model': model,
            'prompt': message,
            'stream': False
        }, timeout=60)
        
        result = response.json()
        return jsonify({'response': result.get('response', 'No response')})
    except Exception as e:
        return jsonify({'response': f'Error: {str(e)}'}), 500

if __name__ == '__main__':
    print('Dashboard v3 starting on http://localhost:5002')
    app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
