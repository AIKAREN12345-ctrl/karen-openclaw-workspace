# Multi-Project Docker Architecture for OpenClaw
**Date:** 2026-03-05
**Purpose:** Scalable architecture for multiple simultaneous research projects

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    Host Machine (24GB RAM)                   │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Project A  │  │  Project B  │  │  Project C  │         │
│  │  (Research) │  │  (Personal) │  │  (Business) │         │
│  │             │  │             │  │             │         │
│  │ ┌─────────┐ │  │ ┌─────────┐ │  │ ┌─────────┐ │         │
│  │ │OpenClaw │ │  │ │OpenClaw │ │  │ │OpenClaw │ │         │
│  │ │Gateway  │ │  │ │Gateway  │ │  │ │Gateway  │ │         │
│  │ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │         │
│  │      │      │  │      │      │  │      │      │         │
│  │ ┌────┴────┐ │  │ ┌────┴────┐ │  │ ┌────┴────┐ │         │
│  │ │  Ollama │ │  │ │  Ollama │ │  │ │  Ollama │ │         │
│  │ │ (7B/14B)│ │  │ │ (7B)    │ │  │ │ (14B)   │ │         │
│  │ └────┬────┘ │  │ └────┬────┘ │  │ └────┬────┘ │         │
│  │      │      │  │      │      │  │      │      │         │
│  │ ┌────┴────┐ │  │ ┌────┴────┐ │  │ ┌────┴────┐ │         │
│  │ │ChromaDB │ │  │ │ChromaDB │ │  │ │ChromaDB │ │         │
│  │ │(Vectors)│ │  │ │(Vectors)│ │  │ │(Vectors)│ │         │
│  │ └─────────┘ │  │ └─────────┘ │  │ └─────────┘ │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                              │
│  Shared Services (Optional):                                 │
│  ┌─────────────────────────────────────────────────────┐    │
│  │  Reverse Proxy (nginx/traefik) - Routes traffic      │    │
│  │  Monitoring (Prometheus/Grafana) - Metrics           │    │
│  │  Shared Storage (NAS/Cloud) - Backups               │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
~/docker-projects/
├── project-a-research/
│   ├── docker-compose.yml
│   ├── .env
│   ├── openclaw-config/
│   └── data/
├── project-b-personal/
│   ├── docker-compose.yml
│   ├── .env
│   ├── openclaw-config/
│   └── data/
├── project-c-business/
│   ├── docker-compose.yml
│   ├── .env
│   ├── openclaw-config/
│   └── data/
└── shared/
    ├── nginx/
    └── monitoring/
```

## Docker Compose Template (Per Project)

```yaml
# project-a-research/docker-compose.yml
version: "3.8"

services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: project-a-openclaw
    ports:
      - "${OPENCLAW_PORT}:18788"
    volumes:
      - ./openclaw-config:/home/node/.openclaw
      - ./data:/home/node/data
    environment:
      - KIMI_API_KEY=${KIMI_API_KEY}
      - OLLAMA_HOST=http://ollama:11434
    networks:
      - project-a-network
    depends_on:
      - ollama
      - chroma
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '1.0'

  ollama:
    image: ollama/ollama:latest
    container_name: project-a-ollama
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=2
      - OLLAMA_MAX_LOADED_MODELS=2
    networks:
      - project-a-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 12G
          cpus: '4.0'
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  chroma:
    image: chromadb/chroma:latest
    container_name: project-a-chroma
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=false
      - IS_PERSISTENT=TRUE
    networks:
      - project-a-network
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '0.5'

networks:
  project-a-network:
    driver: bridge

volumes:
  ollama_data:
  chroma_data:
```

## Environment Configuration (.env)

```bash
# project-a-research/.env
PROJECT_NAME=research-team-alpha
OPENCLAW_PORT=18788
KIMI_API_KEY=sk-...
OLLAMA_MODELS=qwen2.5:14b,nomic-embed-text
MEMORY_LIMIT=12G
CPU_LIMIT=4
```

## Resource Allocation Strategy

| Project | RAM | CPU | GPU | Use Case |
|---------|-----|-----|-----|----------|
| Project A | 12GB | 4 cores | 50% | Heavy research (14B models) |
| Project B | 6GB | 2 cores | 25% | Personal use (7B models) |
| Project C | 4GB | 2 cores | 25% | Business automation |
| **Total** | **22GB** | **8 cores** | **100%** | **Within 24GB limit** |

## Management Commands

```bash
# Start a project
cd ~/docker-projects/project-a-research
docker-compose up -d

# Stop a project
docker-compose down

# View logs
docker-compose logs -f openclaw

# Scale Ollama (if needed)
docker-compose up -d --scale ollama=2

# Backup project data
docker-compose exec openclaw tar czf /backup/project-a-$(date +%Y%m%d).tar.gz /home/node/.openclaw

# List all running projects
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Benefits of This Architecture

1. **Complete Isolation** — Each project is independent
2. **Resource Control** — Hard limits prevent runaway usage
3. **Easy Scaling** — Add/remove projects as needed
4. **Version Control** — Each project has its own config
5. **Backup/Restore** — Per-project data management
6. **Team Ready** — Different users can own different projects

## Migration Path from Current Setup

### Phase 1: Prepare (Week 1)
- Install Docker Desktop on Windows
- Enable WSL2 backend
- Test with single project

### Phase 2: Migrate Main Project (Week 2)
- Export current OpenClaw config
- Create docker-compose.yml
- Import data to container
- Verify everything works

### Phase 3: Add Projects (Week 3+)
- Create additional project directories
- Copy and customize docker-compose.yml
- Start new projects
- Allocate resources appropriately

## Cost Comparison

| Approach | Monthly Cost | Complexity | Scalability |
|----------|-------------|------------|-------------|
| Current (hybrid) | ~$20-30 | Low | Limited |
| All Kimi | ~$100-200 | Low | Medium |
| Docker + Local | ~$0-10 | Medium | High |
| Docker + Hybrid | ~$20-30 | Medium | High |

## Recommendation

**Start with Docker when:**
- You need 3+ separate research contexts
- Team members need isolated environments
- You want to experiment without risk to main system
- Resource contention becomes a problem

**Current setup is fine when:**
- Single user, single project
- Happy with hybrid Kimi/Ollama approach
- Don't want to learn Docker

## Next Steps

1. **Try Docker** — Install Docker Desktop, test single project
2. **Evaluate** — Compare performance, ease of use
3. **Decide** — Migrate if benefits outweigh complexity
4. **Scale** — Add projects as needed

---

*This architecture provides enterprise-grade isolation and scalability for personal AI research.*
