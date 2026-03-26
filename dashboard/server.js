const express = require('express');
const WebSocket = require('ws');
const http = require('http');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

const PORT = process.env.PORT || 3000;
const DATA_DIR = path.join(__dirname, 'data');
const MEMORY_DIR = path.join(__dirname, '..', 'memory');

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Store connected clients
const clients = new Set();

// WebSocket handling
wss.on('connection', (ws) => {
  clients.add(ws);
  console.log('Client connected');
  
  ws.on('close', () => {
    clients.delete(ws);
    console.log('Client disconnected');
  });
});

// Broadcast to all clients
function broadcast(data) {
  const message = JSON.stringify(data);
  clients.forEach(client => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(message);
    }
  });
}

// Routes

// Get all projects
app.get('/api/projects', async (req, res) => {
  try {
    const projectsPath = path.join(DATA_DIR, 'projects.json');
    const data = await fs.readFile(projectsPath, 'utf8').catch(() => '[]');
    res.json(JSON.parse(data));
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Create new project
app.post('/api/projects', async (req, res) => {
  try {
    const projectsPath = path.join(DATA_DIR, 'projects.json');
    const data = await fs.readFile(projectsPath, 'utf8').catch(() => '[]');
    const projects = JSON.parse(data);
    
    const newProject = {
      id: Date.now().toString(),
      ...req.body,
      createdAt: new Date().toISOString(),
      status: 'todo'
    };
    
    projects.push(newProject);
    await fs.writeFile(projectsPath, JSON.stringify(projects, null, 2));
    
    broadcast({ type: 'project-created', project: newProject });
    res.json(newProject);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Update project
app.put('/api/projects/:id', async (req, res) => {
  try {
    const projectsPath = path.join(DATA_DIR, 'projects.json');
    const data = await fs.readFile(projectsPath, 'utf8').catch(() => '[]');
    const projects = JSON.parse(data);
    
    const index = projects.findIndex(p => p.id === req.params.id);
    if (index === -1) {
      return res.status(404).json({ error: 'Project not found' });
    }
    
    projects[index] = { ...projects[index], ...req.body, updatedAt: new Date().toISOString() };
    await fs.writeFile(projectsPath, JSON.stringify(projects, null, 2));
    
    broadcast({ type: 'project-updated', project: projects[index] });
    res.json(projects[index]);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Delete project
app.delete('/api/projects/:id', async (req, res) => {
  try {
    const projectsPath = path.join(DATA_DIR, 'projects.json');
    const data = await fs.readFile(projectsPath, 'utf8').catch(() => '[]');
    const projects = JSON.parse(data);
    
    const filtered = projects.filter(p => p.id !== req.params.id);
    await fs.writeFile(projectsPath, JSON.stringify(filtered, null, 2));
    
    broadcast({ type: 'project-deleted', id: req.params.id });
    res.json({ success: true });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get research history
app.get('/api/research', async (req, res) => {
  try {
    const researchDir = path.join(MEMORY_DIR, 'research');
    const files = await fs.readdir(researchDir).catch(() => []);
    
    const research = [];
    for (const file of files.filter(f => f.endsWith('.md'))) {
      const [date, topic] = file.replace('.md', '').split('_');
      const stat = await fs.stat(path.join(researchDir, file));
      research.push({
        file,
        date,
        topic: topic || 'general',
        size: stat.size,
        modified: stat.mtime
      });
    }
    
    research.sort((a, b) => new Date(b.date) - new Date(a.date));
    res.json(research);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get research content
app.get('/api/research/:file', async (req, res) => {
  try {
    const filePath = path.join(MEMORY_DIR, 'research', req.params.file);
    const content = await fs.readFile(filePath, 'utf8');
    res.json({ content });
  } catch (error) {
    res.status(404).json({ error: 'Research not found' });
  }
});

// Spawn research
app.post('/api/research/spawn', async (req, res) => {
  try {
    const { topic } = req.body;
    
    // Map topic to search query
    const queries = {
      openclaw: 'OpenClaw updates news',
      'ai-models': 'new AI models releases 2026',
      income: 'AI passive income opportunities',
      philosophy: 'John Demartini Eckhart Tolle quotes'
    };
    
    const query = queries[topic] || topic;
    const today = new Date().toISOString().split('T')[0];
    const filename = `${today}_${topic}.md`;
    const filepath = path.join(MEMORY_DIR, 'research', filename);
    
    // Check if already exists today
    try {
      await fs.access(filepath);
      return res.json({ success: true, topic, message: 'Research already exists for today' });
    } catch {
      // File doesn't exist, continue
    }
    
    // Spawn OpenClaw subagent via sessions_spawn
    const { spawn } = require('child_process');
    const openclawPath = process.env.OPENCLAW_PATH || 'openclaw';
    
    // Create a temporary script to spawn research
    const scriptContent = `
const { sessions_spawn } = require('${openclawPath}');

sessions_spawn({
  mode: 'run',
  runtime: 'subagent',
  task: \`Research ${query} using ONLY web_fetch with DuckDuckGo URLs. DO NOT use web_search. Save results to memory/research/${filename} (append if exists).\`
}).then(result => {
  console.log('Research spawned:', result);
}).catch(err => {
  console.error('Failed to spawn research:', err);
});
`;
    
    // For now, just create a placeholder file and return success
    // In a real implementation, you'd integrate with OpenClaw's API
    const placeholder = `# Research: ${topic}\n\nDate: ${today}\n\nStatus: Research queued...\n\nThis research was spawned from the dashboard.\n`;
    await fs.writeFile(filepath, placeholder);
    
    broadcast({ type: 'research-started', topic });
    res.json({ success: true, topic, message: 'Research queued' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// System status
app.get('/api/system/status', async (req, res) => {
  try {
    const status = await getSystemStatus();
    res.json(status);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Memory search
app.get('/api/memory/search', async (req, res) => {
  try {
    const { query } = req.query;
    if (!query) {
      return res.json({ query: '', results: [] });
    }
    
    // Search through memory files
    const results = [];
    const memoryDir = MEMORY_DIR;
    
    // Search in daily memory files
    const files = await fs.readdir(memoryDir).catch(() => []);
    const mdFiles = files.filter(f => f.endsWith('.md') && !f.startsWith('research/'));
    
    for (const file of mdFiles.slice(0, 30)) { // Limit to recent 30 files
      try {
        const content = await fs.readFile(path.join(memoryDir, file), 'utf8');
        const lowerContent = content.toLowerCase();
        const lowerQuery = query.toLowerCase();
        
        if (lowerContent.includes(lowerQuery)) {
          // Calculate simple relevance score
          const occurrences = (lowerContent.match(new RegExp(lowerQuery, 'g')) || []).length;
          const score = Math.min(occurrences / 10, 1); // Normalize to 0-1
          
          // Extract snippet around first occurrence
          const index = lowerContent.indexOf(lowerQuery);
          const start = Math.max(0, index - 100);
          const end = Math.min(content.length, index + 200);
          const snippet = content.substring(start, end).replace(/\n/g, ' ');
          
          results.push({
            title: file.replace('.md', ''),
            content: snippet + '...',
            date: file.replace('.md', ''),
            score: score,
            file
          });
        }
      } catch (err) {
        // Skip files that can't be read
      }
    }
    
    // Sort by relevance
    results.sort((a, b) => b.score - a.score);
    
    res.json({ query, results: results.slice(0, 10) }); // Return top 10
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Get today's briefing
app.get('/api/briefing/today', async (req, res) => {
  try {
    const today = new Date().toISOString().split('T')[0];
    const briefingPath = path.join(MEMORY_DIR, `${today}.md`);
    const content = await fs.readFile(briefingPath, 'utf8').catch(() => '# No briefing for today');
    res.json({ date: today, content });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Helper functions
async function spawnResearch(topic) {
  // This would call OpenClaw to spawn a research subagent
  // For now, return a placeholder
  return { topic, status: 'started' };
}

async function getSystemStatus() {
  // Get OpenClaw status, Ollama status, etc.
  return {
    openclaw: { version: '2026.3.2', status: 'running' },
    ollama: { status: 'available', models: ['qwen2.5:14b', 'nomic-embed-text'] },
    timestamp: new Date().toISOString()
  };
}

// Initialize data files
async function init() {
  try {
    await fs.mkdir(DATA_DIR, { recursive: true });
    
    const projectsPath = path.join(DATA_DIR, 'projects.json');
    try {
      await fs.access(projectsPath);
    } catch {
      await fs.writeFile(projectsPath, '[]');
    }
  } catch (error) {
    console.error('Init error:', error);
  }
}

init().then(() => {
  server.listen(PORT, () => {
    console.log(`Dashboard server running on http://localhost:${PORT}`);
  });
});
