const express = require('express');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// Cache for data
let cachedData = {
    timestamp: null,
    data: null
};

// Fetch OpenClaw status
async function getOpenClawStatus() {
    return new Promise((resolve, reject) => {
        exec('openclaw status --json', { encoding: 'utf8' }, (error, stdout) => {
            if (error) {
                reject(error);
                return;
            }
            try {
                const data = JSON.parse(stdout);
                resolve(data);
            } catch (e) {
                reject(e);
            }
        });
    });
}

// Fetch Ollama status
async function getOllamaStatus() {
    return new Promise((resolve) => {
        exec('ollama list', { encoding: 'utf8' }, (error, stdout) => {
            if (error) {
                resolve({ running: false, models: [] });
                return;
            }
            const models = stdout.split('\n')
                .slice(1) // Skip header
                .filter(line => line.trim())
                .map(line => {
                    const parts = line.split(/\s+/);
                    return {
                        name: parts[0],
                        size: parts[2] + ' ' + parts[3]
                    };
                });
            resolve({ running: true, models });
        });
    });
}

// Fetch disk usage
async function getDiskUsage() {
    return new Promise((resolve) => {
        exec('wmic logicaldisk get size,freespace,caption', { encoding: 'utf8' }, (error, stdout) => {
            if (error) {
                resolve({ total: 0, free: 0, used: 0 });
                return;
            }
            const lines = stdout.trim().split('\n').slice(1);
            let total = 0, free = 0;
            lines.forEach(line => {
                const parts = line.trim().split(/\s+/);
                if (parts.length >= 3) {
                    free += parseInt(parts[1]) || 0;
                    total += parseInt(parts[2]) || 0;
                }
            });
            resolve({
                total: Math.round(total / (1024**3)),
                free: Math.round(free / (1024**3)),
                used: Math.round((total - free) / (1024**3))
            });
        });
    });
}

// Fetch GitHub commits
async function getGitHubCommits() {
    return new Promise((resolve) => {
        exec('git log --oneline -10 --pretty=format:"%h|%s|%ar"', { 
            cwd: path.join(__dirname, '..'),
            encoding: 'utf8' 
        }, (error, stdout) => {
            if (error) {
                resolve([]);
                return;
            }
            const commits = stdout.split('\n')
                .filter(line => line.trim())
                .map(line => {
                    const parts = line.split('|');
                    return {
                        hash: parts[0],
                        message: parts[1],
                        time: parts[2]
                    };
                });
            resolve(commits);
        });
    });
}

// Fetch cron jobs
async function getCronJobs() {
    return new Promise((resolve) => {
        exec('openclaw cron list --json', { encoding: 'utf8' }, (error, stdout) => {
            if (error) {
                resolve([]);
                return;
            }
            try {
                const jobs = JSON.parse(stdout);
                resolve(jobs);
            } catch (e) {
                resolve([]);
            }
        });
    });
}

// Fetch research files organized by week
async function getResearchFiles() {
    const researchDir = path.join(__dirname, '..', 'memory', 'research');
    
    return new Promise((resolve) => {
        fs.readdir(researchDir, (err, files) => {
            if (err) {
                resolve({});
                return;
            }
            
            // Filter .md files and organize by week
            const mdFiles = files.filter(f => f.endsWith('.md'));
            const organized = {};
            
            mdFiles.forEach(file => {
                // Extract date from filename (YYYY-MM-DD or YYYYMMDD format)
                const dateMatch = file.match(/(\d{4})-?(\d{2})-?(\d{2})/);
                if (dateMatch) {
                    const year = dateMatch[1];
                    const month = dateMatch[2];
                    const day = dateMatch[3];
                    
                    // Calculate week number
                    const date = new Date(year, month - 1, day);
                    const startOfYear = new Date(date.getFullYear(), 0, 1);
                    const weekNumber = Math.ceil((((date - startOfYear) / 86400000) + startOfYear.getDay() + 1) / 7);
                    
                    const weekKey = `${year}-W${weekNumber.toString().padStart(2, '0')}`;
                    
                    if (!organized[weekKey]) {
                        organized[weekKey] = [];
                    }
                    
                    // Extract topic from filename
                    const topic = file
                        .replace(/\d{4}-?\d{2}-?\d{2}_?/, '')
                        .replace(/\.md$/, '')
                        .replace(/_/g, ' ')
                        .replace(/-/g, ' ');
                    
                    organized[weekKey].push({
                        filename: file,
                        topic: topic,
                        date: `${year}-${month}-${day}`,
                        path: `/memory/research/${file}`
                    });
                }
            });
            
            // Sort weeks descending (newest first)
            const sorted = Object.keys(organized)
                .sort((a, b) => b.localeCompare(a))
                .reduce((acc, key) => {
                    acc[key] = organized[key].sort((a, b) => b.date.localeCompare(a.date));
                    return acc;
                }, {});
            
            resolve(sorted);
        });
    });
}
// Aggregate all data
async function fetchAllData() {
    try {
        const [openclaw, ollama, disk, commits, cronJobs, research] = await Promise.all([
            getOpenClawStatus().catch(() => ({ version: '2026.3.2', gateway: { reachable: true, latency: 26 } })),
            getOllamaStatus(),
            getDiskUsage(),
            getGitHubCommits(),
            getCronJobs(),
            getResearchFiles()
        ]);

        return {
            timestamp: new Date().toISOString(),
            system: {
                version: openclaw.version || '2026.3.2',
                gateway: openclaw.gateway?.reachable ? `Online (${openclaw.gateway.latency}ms)` : 'Offline',
                node: openclaw.node?.connected ? 'Connected' : 'Disconnected',
                uptime: openclaw.uptime || 'Unknown',
                sessions: openclaw.sessions?.count || 0
            },
            ollama: {
                running: ollama.running,
                models: ollama.models
            },
            disk: disk,
            github: {
                commits: commits
            },
            cron: cronJobs,
            research: research
        };
    } catch (error) {
        console.error('Error fetching data:', error);
        return cachedData.data || {};
    }
}

// API Routes
app.get('/api/data', async (req, res) => {
    // Cache for 10 seconds
    const now = Date.now();
    if (!cachedData.timestamp || now - cachedData.timestamp > 10000) {
        cachedData.data = await fetchAllData();
        cachedData.timestamp = now;
    }
    res.json(cachedData.data);
});

app.get('/api/refresh', async (req, res) => {
    cachedData.data = await fetchAllData();
    cachedData.timestamp = Date.now();
    res.json(cachedData.data);
});

// Serve dashboard
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Start server
app.listen(PORT, () => {
    console.log(`🦞 Karen Dashboard Server running at http://localhost:${PORT}`);
    console.log('Press Ctrl+C to stop');
});
