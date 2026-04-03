# Karen Dashboard v3

Dynamic dashboard with real-time data from OpenClaw.

## Setup

1. **Install dependencies:**
   ```bash
   cd dashboard
   npm install
   ```

2. **Start the server:**
   ```bash
   npm start
   ```

3. **Open in browser:**
   http://localhost:3000

## Features

- **Real-time data** from OpenClaw API
- **Live updates** every 30 seconds
- **9 organized tabs:**
  - Overview (weather, stats, activity)
  - System (Ollama, disk, API usage)
  - Skills (15 installed)
  - Cron Jobs (with toggles)
  - Memory (search)
  - Logs (errors, learnings)
  - GitHub (recent commits)
  - Weather (Dublin)
  - Security (audit, issues)

## API Endpoints

- `GET /api/data` - Fetch all dashboard data (cached 10s)
- `GET /api/refresh` - Force refresh data

## Data Sources

- OpenClaw status
- Ollama models
- Disk usage (Windows)
- Git commits
- Cron jobs

## Auto-refresh

Dashboard automatically refreshes every 30 seconds.
Pauses when tab is hidden to save resources.
