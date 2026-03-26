# Interactive Dashboard for OpenClaw

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Dashboard Server (Node.js)                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Web UI     │  │  API        │  │  WebSocket  │         │
│  │  (Static)   │  │  (REST)     │  │  (Live)     │         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘         │
│         └─────────────────┼─────────────────┘                │
│                           │                                  │
│         ┌─────────────────┘                                  │
│         ▼                                                    │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Project    │  │  Research   │  │  System     │         │
│  │  Manager    │  │  Tracker    │  │  Monitor    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└───────────────────────────┬─────────────────────────────────┘
                            │
         ┌──────────────────┼──────────────────┐
         ▼                  ▼                  ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│  OpenClaw   │    │  Memory     │    │  Ollama     │
│  Gateway    │    │  Files      │    │  (Local)    │
└─────────────┘    └─────────────┘    └─────────────┘
```

## Features

### 1. Project Management
- Create/edit/delete projects
- Kanban board (To Do / In Progress / Done)
- Priority levels (High/Medium/Low)
- Due dates and milestones
- Tags and categories

### 2. Research Automation
- View active/completed research
- Spawn new research subagents
- Filter by topic (AI, OpenClaw, Income, etc.)
- View research results inline
- Download research files

### 3. System Status
- OpenClaw version and health
- Ollama status (models loaded)
- Memory search status
- Active subagents/sessions
- Recent errors/logs

### 4. Quick Actions
- Spawn research (buttons for each topic)
- Run system checks
- View daily briefings
- Check calendar
- Memory search

### 5. Live Updates
- WebSocket connection for real-time updates
- Research completion notifications
- System status changes
- New memory entries

## API Endpoints

```
GET  /api/projects              - List all projects
POST /api/projects              - Create new project
PUT  /api/projects/:id          - Update project
DELETE /api/projects/:id        - Delete project

GET  /api/research              - List research history
POST /api/research/spawn        - Spawn research subagent
GET  /api/research/:id          - Get research details

GET  /api/system/status         - System health check
GET  /api/system/logs           - Recent logs
POST /api/system/restart        - Restart gateway

GET  /api/memory/search         - Search memory
POST /api/memory/index          - Reindex memory

GET  /api/briefing/today        - Today's briefing
GET  /api/briefing/yesterday    - Yesterday's summary

WebSocket /ws                   - Live updates
```

## Tech Stack

- **Backend:** Node.js + Express
- **Frontend:** Vanilla JS (no framework bloat)
- **Styling:** Tailwind-like CSS (custom)
- **Real-time:** WebSocket (ws library)
- **Data:** JSON files (projects, config)

## File Structure

```
dashboard/
├── server.js           # Main server
├── package.json        # Dependencies
├── config.json         # Dashboard config
├── public/
│   ├── index.html      # Main page
│   ├── css/
│   │   └── style.css   # Styles
│   ├── js/
│   │   ├── app.js      # Main app
│   │   ├── api.js      # API client
│   │   ├── ws.js       # WebSocket handler
│   │   ├── projects.js # Project manager
│   │   ├── research.js # Research tracker
│   │   └── system.js   # System monitor
│   └── assets/
│       └── icons/      # UI icons
├── data/
│   ├── projects.json   # Project data
│   └── config.json     # User config
└── routes/
    ├── projects.js     # Project routes
    ├── research.js     # Research routes
    ├── system.js       # System routes
    └── memory.js       # Memory routes
```

## Implementation Plan

### Phase 1: Core Server (30 min)
- [ ] Set up Express server
- [ ] Create API routes structure
- [ ] Add WebSocket support
- [ ] Connect to OpenClaw gateway

### Phase 2: Frontend UI (45 min)
- [ ] Build main layout
- [ ] Project kanban board
- [ ] Research feed
- [ ] System status panel
- [ ] Quick action buttons

### Phase 3: Integration (30 min)
- [ ] Connect API to OpenClaw
- [ ] Real-time updates via WebSocket
- [ ] Test all features
- [ ] Add error handling

### Phase 4: Polish (15 min)
- [ ] Dark mode
- [ ] Mobile responsive
- [ ] Loading states
- [ ] Error messages

Total: ~2 hours for working prototype

## Next Steps

1. **Approve architecture** — Does this match what you want?
2. **Choose port** — What port should it run on? (suggest 3000 or 8080)
3. **Start building** — I'll create the server and UI

Ready to proceed?
