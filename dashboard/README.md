# Karen Dashboard

A web-based dashboard for monitoring and controlling the Karen system.

## Features

- **System Overview**: Real-time status of all components
- **Research Control**: Trigger research jobs manually
- **Model Management**: Switch between AI models
- **Memory Browser**: View and search memory files
- **Logs Viewer**: Real-time log streaming
- **Cron Management**: View and manage scheduled jobs

## Installation

```bash
cd dashboard
pip install -r requirements.txt
python app.py
```

## Access

- **Local**: http://localhost:5000
- **Network**: http://100.75.72.26:5000 (if firewall allows)

## Authentication

Default credentials (change in production):
- Username: `admin`
- Password: `karen2026`

## API Endpoints

- `GET /api/status` - System status
- `POST /api/research/trigger` - Trigger research job
- `GET /api/models` - List available models
- `POST /api/models/switch` - Switch active model
- `GET /api/memory` - List memory files
- `GET /api/logs` - Stream logs

