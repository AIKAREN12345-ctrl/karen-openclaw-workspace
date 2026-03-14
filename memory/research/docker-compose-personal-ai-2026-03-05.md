# Docker Compose for Personal AI Systems - Research Report

**Date:** 2026-03-05  
**Research Focus:** Docker Compose orchestration for personal AI stacks (OpenClaw + Ollama + ChromaDB)

---

## Executive Summary

Docker Compose offers significant benefits for personal AI systems when you need reproducibility, multi-service orchestration, or remote access. However, for single-user, single-machine setups (especially on macOS), native installations may be simpler and more performant.

**Recommendation for our setup:** Docker is worth considering if we plan to add more services (vector DB, web UI) or need consistent deployments across environments. For a simple OpenClaw + Ollama setup on Windows, native installation may be more straightforward.

---

## 1. Docker Compose Basics & YAML Configuration

### What is Docker Compose?
Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you use a YAML file to configure your application's services, then create and start all services with a single command.

### Key YAML Structure
```yaml
version: "3.8"  # Compose file format version

services:
  # Define containers here
  
volumes:
  # Define named volumes here
  
networks:
  # Define custom networks here
```

### Essential Configuration Options

| Option | Purpose | Example |
|--------|---------|---------|
| `image` | Base container image | `image: ollama/ollama:latest` |
| `container_name` | Human-readable name | `container_name: ai-ollama` |
| `ports` | Port mapping host:container | `"11434:11434"` |
| `volumes` | Persistent storage | `ollama_data:/root/.ollama` |
| `environment` | Environment variables | `OLLAMA_NUM_PARALLEL=4` |
| `depends_on` | Startup order | `depends_on: [ollama]` |
| `restart` | Auto-restart policy | `restart: unless-stopped` |
| `networks` | Custom networking | `networks: [ai-network]` |

### Complete Example: Ollama + ChromaDB Stack
```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ai-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    networks:
      - ai-network
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  chroma:
    image: chromadb/chroma:latest
    container_name: ai-chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=false
      - IS_PERSISTENT=TRUE
    networks:
      - ai-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: ai-webui
    ports:
      - "3000:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    networks:
      - ai-network
    depends_on:
      ollama:
        condition: service_healthy
    restart: unless-stopped

volumes:
  ollama_data:
  chroma_data:
  open_webui_data:

networks:
  ai-network:
    driver: bridge
```

---

## 2. Complete Stack: OpenClaw + Ollama + ChromaDB

### Architecture Overview
```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Network: ai-network                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │   OpenClaw   │  │    Ollama    │  │    ChromaDB      │  │
│  │   (Host)     │◄─┤   :11434     │  │    :8000         │  │
│  │              │  │              │  │                  │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
│         │                 │                    │            │
│         └─────────────────┴────────────────────┘            │
│                      Named Volumes                          │
└─────────────────────────────────────────────────────────────┘
```

### Important Note on OpenClaw
OpenClaw is a Windows-based AI assistant platform that runs natively on the host. Unlike other services, it cannot be easily containerized because it requires:
- Direct Windows system integration
- Access to host tools and browsers
- Telegram/Discord bot connectivity

**Recommended approach:** Run OpenClaw natively on Windows, connect to containerized Ollama and ChromaDB via exposed ports.

### Docker Compose for Ollama + ChromaDB (Supporting Services)
```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
        limits:
          memory: 16G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  chroma:
    image: chromadb/chroma:latest
    container_name: chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=false
      - IS_PERSISTENT=TRUE
      - CHROMA_SERVER_AUTHN_PROVIDER=${CHROMA_AUTH_PROVIDER:-}
      - CHROMA_SERVER_AUTHN_CREDENTIALS=${CHROMA_AUTH_TOKEN:-}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  # Optional: Web UI for Ollama
  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
      - RAG_EMBEDDING_ENGINE=ollama
      - RAG_EMBEDDING_MODEL=nomic-embed-text
      - VECTOR_DB=chroma
      - CHROMA_HTTP_HOST=chroma
      - CHROMA_HTTP_PORT=8000
    depends_on:
      ollama:
        condition: service_healthy
      chroma:
        condition: service_healthy
    restart: unless-stopped

volumes:
  ollama_data:
    driver: local
  chroma_data:
    driver: local
  open_webui_data:
    driver: local

networks:
  default:
    driver: bridge
```

### Connecting OpenClaw to Docker Services
OpenClaw running natively on Windows can connect to containerized services using `localhost`:

```python
# OpenClaw configuration for Dockerized Ollama/Chroma
OLLAMA_HOST = "http://localhost:11434"
CHROMA_HOST = "http://localhost:8000"

# Example: Using Ollama from OpenClaw
import requests

def generate_with_ollama(prompt, model="qwen2.5:14b"):
    response = requests.post(
        f"{OLLAMA_HOST}/api/generate",
        json={
            "model": model,
            "prompt": prompt,
            "stream": False
        }
    )
    return response.json()["response"]

# Example: Using ChromaDB from OpenClaw
import chromadb

chroma_client = chromadb.HttpClient(host="localhost", port=8000)
collection = chroma_client.get_or_create_collection("memory")
```

---

## 3. Environment Variables and Secrets Management

### The .env File Pattern
Create a `.env` file in the same directory as `docker-compose.yml`:

```bash
# .env - DO NOT COMMIT TO GIT
POSTGRES_PASSWORD=your_secure_password_here
CHROMA_AUTH_TOKEN=your-secret-token
OLLAMA_API_KEY=sk-ollama-...
OPENAI_API_KEY=sk-...  # For fallback/embeddings
```

Reference in docker-compose.yml:
```yaml
services:
  postgres:
    environment:
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-changeme}
```

**Security best practices:**
1. Add `.env` to `.gitignore`
2. Use `${VAR:-default}` syntax for fallbacks
3. Never commit secrets to version control
4. For production, use Docker Secrets (requires Swarm) or external vaults

### Docker Secrets (Production)
For production deployments with Docker Swarm:
```yaml
services:
  app:
    secrets:
      - db_password
      - api_key

secrets:
  db_password:
    external: true
  api_key:
    file: ./secrets/api_key.txt
```

### Environment Variable Precedence
1. Command line: `VAR=value docker compose up`
2. `.env` file in project directory
3. Shell environment variables
4. Docker Compose file defaults

---

## 4. Auto-Restart, Health Checks, and Monitoring

### Restart Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `no` | Never restart | Default, manual control |
| `always` | Always restart | Critical services |
| `unless-stopped` | Restart unless manually stopped | Recommended for most services |
| `on-failure` | Restart on error only | Debugging, non-critical |

**Recommendation:** Use `restart: unless-stopped` for AI services. It provides resilience while respecting manual intervention.

### Health Checks
Health checks prevent dependent services from starting before dependencies are ready:

```yaml
services:
  ollama:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s      # Check every 30 seconds
      timeout: 10s       # Wait 10 seconds for response
      retries: 3         # Mark unhealthy after 3 failures
      start_period: 40s  # Grace period for startup
```

Common health check commands:
```bash
# Ollama
curl -f http://localhost:11434/api/tags

# ChromaDB
curl -f http://localhost:8000/api/v1/heartbeat

# PostgreSQL
pg_isready -U username -d database

# Redis
redis-cli ping

# Generic HTTP
curl -f http://localhost:PORT/health || exit 1
```

### Service Dependencies
```yaml
services:
  app:
    depends_on:
      ollama:
        condition: service_healthy  # Wait for health check
      chroma:
        condition: service_healthy
```

### Log Management
Prevent logs from consuming disk space:
```yaml
services:
  ollama:
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"
```

### Auto-Updates with Watchtower
```yaml
services:
  watchtower:
    image: containrrr/watchtower
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_CLEANUP=true
      - WATCHTOWER_SCHEDULE=0 0 4 * * *  # 4 AM daily
      - WATCHTOWER_INCLUDE_STOPPED=true
      - WATCHTOWER_REVIVE_STOPPED=true
    restart: unless-stopped
```

**Warning:** Auto-updates can introduce breaking changes. For stability-critical setups, update manually.

---

## 5. Backup and Restore Strategies

### Named Volume Backups

#### Method 1: Using tar (Recommended)
```bash
# Backup Ollama models
docker run --rm \
  -v ollama_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/ollama-backup-$(date +%Y%m%d).tar.gz -C /data .

# Backup ChromaDB
docker run --rm \
  -v chroma_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/chroma-backup-$(date +%Y%m%d).tar.gz -C /data .
```

#### Method 2: Using docker-compose
```bash
# Create backup script
#!/bin/bash
# backup-volumes.sh
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"
mkdir -p $BACKUP_DIR

# Stop services gracefully
docker compose stop

# Backup each volume
for volume in ollama_data chroma_data open_webui_data; do
  docker run --rm \
    -v ${volume}:/data \
    -v $(pwd)/backups:/backup \
    alpine tar czf /backup/${volume}-${DATE}.tar.gz -C /data .
  echo "Backed up $volume"
done

# Restart services
docker compose start

echo "Backup complete: $BACKUP_DIR"
```

#### Method 3: Automated with cron
```bash
# Add to crontab (runs daily at 2 AM)
0 2 * * * cd /path/to/ai-stack && ./backup-volumes.sh >> /var/log/ai-backup.log 2>&1
```

### Restore from Backup
```bash
# Restore Ollama data
docker run --rm \
  -v ollama_data:/data \
  -v $(pwd):/backup \
  alpine sh -c "cd /data && tar xzf /backup/ollama-backup-20260305.tar.gz"

# Or using docker-compose
docker compose down
docker volume rm ai-stack_ollama_data
docker volume create ai-stack_ollama_data
docker run --rm -v ai-stack_ollama_data:/data -v $(pwd)/backups:/backup alpine tar xzf /backup/ollama-backup-20260305.tar.gz -C /data
docker compose up -d
```

### Bind Mount Alternative (Easier Backups)
If you prefer easier file-level backups, use bind mounts:
```yaml
services:
  ollama:
    volumes:
      - ./data/ollama:/root/.ollama  # Bind mount instead of named volume
```

**Trade-offs:**
- Named volumes: Better Docker integration, harder to access directly
- Bind mounts: Easier to backup/inspect, potential permission issues

### Cloud Backup Integration
```bash
# Backup to S3 (using AWS CLI container)
docker run --rm \
  -v ollama_data:/data \
  -v ~/.aws:/root/.aws \
  amazon/aws-cli \
  s3 sync /data s3://your-bucket/ollama-backup/
```

---

## 6. When Docker is Worth It vs Overkill

### Use Docker When:

| Scenario | Why Docker Helps |
|----------|------------------|
| **Multi-service stack** | Ollama + Chroma + WebUI + more in one command |
| **Team/Shared environment** | Same setup on every machine |
| **Headless server** | Remote GPU server, access from laptop |
| **Homelab/NAS** | Compose is the native language of homelabs |
| **Development/Testing** | Easy teardown, clean slate, reproducible |
| **CI/CD pipelines** | Consistent environments |
| **Multiple projects** | Isolation between different AI projects |

### Skip Docker When:

| Scenario | Why Native is Better |
|----------|---------------------|
| **Single user, single machine** | Native Ollama is simpler, zero overhead |
| **macOS (Apple Silicon)** | Docker can't access GPU - runs on CPU only |
| **Maximum performance** | No container overhead, direct hardware access |
| **Quick experimentation** | One-time setup, no need for reproducibility |
| **Limited disk space** | Docker images consume extra space |
| **Learning/debugging** | Fewer layers to troubleshoot |

### Decision Matrix for Our Setup

| Factor | Our Situation | Docker? |
|--------|--------------|---------|
| Single user | Yes | Neutral |
| Windows 11 | Yes | Good |
| May add ChromaDB | Likely | Good |
| May add WebUI | Possible | Good |
| GPU available | Yes (NVIDIA) | Good |
| Need reproducibility | Maybe | Good |
| Simple setup priority | High | Neutral |

**Verdict:** Docker is worth it if we plan to expand beyond just Ollama. For OpenClaw + Ollama only, native installation is simpler.

---

## 7. Hardware Requirements and Resource Optimization

### Minimum Requirements

| Component | Minimum | Recommended | Notes |
|-----------|---------|-------------|-------|
| RAM | 8 GB | 16-32 GB | 7B models need ~8GB, 13B+ need 16GB+ |
| Storage | 50 GB | 100+ GB | Models are 2-40 GB each |
| GPU VRAM | 8 GB | 12-24 GB | For GPU acceleration |
| CPU | 4 cores | 8+ cores | For CPU-only fallback |

### Model Size vs Resource Usage

| Model Size | Quantization | RAM Needed | VRAM Needed | Disk Usage |
|------------|--------------|------------|-------------|------------|
| 3B | Q4_K_M | ~4 GB | ~3 GB | ~2 GB |
| 7-8B | Q4_K_M | ~8 GB | ~6 GB | ~4.5 GB |
| 14B | Q4_K_M | ~16 GB | ~10 GB | ~8 GB |
| 32B | Q4_K_M | ~32 GB | ~20 GB | ~18 GB |
| 70B | Q4_K_M | ~64 GB | ~40 GB | ~40 GB |

### Resource Limits in Docker Compose
```yaml
services:
  ollama:
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### Performance Optimization Tips

1. **Use GPU acceleration** - Essential for usable performance
   ```yaml
   deploy:
     resources:
       reservations:
         devices:
           - driver: nvidia
             count: all
             capabilities: [gpu]
   ```

2. **Enable parallel processing**
   ```yaml
   environment:
     - OLLAMA_NUM_PARALLEL=4
     - OLLAMA_MAX_LOADED_MODELS=3
   ```

3. **Use named volumes on fast storage** - NVMe SSD recommended

4. **Limit loaded models** - Prevents OOM errors
   ```yaml
   environment:
     - OLLAMA_MAX_LOADED_MODELS=2
   ```

5. **Choose appropriate models** - Smaller quantized models for most tasks

### Windows-Specific Considerations

- **WSL2 backend:** Docker Desktop on Windows uses WSL2. Ensure WSL2 has sufficient memory:
  ```
  # In %UserProfile%\.wslconfig
  [wsl2]
  memory=16GB
  processors=8
  ```

- **GPU passthrough:** NVIDIA Container Toolkit required for GPU access

- **Port binding:** Windows Firewall may block container ports

---

## 8. Ready-to-Use Examples

### Example 1: Minimal Ollama Only
```yaml
version: "3.8"
services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    restart: unless-stopped

volumes:
  ollama_data:
```

### Example 2: Full AI Stack with Open WebUI
```yaml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_NUM_PARALLEL=4
      - OLLAMA_MAX_LOADED_MODELS=3
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    restart: unless-stopped

  chroma:
    image: chromadb/chroma:latest
    container_name: chroma
    ports:
      - "8000:8000"
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - ANONYMIZED_TELEMETRY=false
      - IS_PERSISTENT=TRUE
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/heartbeat"]
      interval: 10s
      timeout: 5s
      retries: 5
    restart: unless-stopped

  open-webui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: open-webui
    ports:
      - "3000:8080"
    volumes:
      - open_webui_data:/app/backend/data
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      ollama:
        condition: service_healthy
    restart: unless-stopped

volumes:
  ollama_data:
  chroma_data:
  open_webui_data:
```

### Example 3: Development Override File
```yaml
# docker-compose.override.yml (auto-loaded with main file)
version: "3.8"

services:
  ollama:
    # Mount local modelfiles for development
    volumes:
      - ollama_data:/root/.ollama
      - ./modelfiles:/modelfiles
    
  app:
    build:
      context: ./app
    volumes:
      - ./app:/code
    command: uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Example 4: Production Configuration
```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  ollama:
    image: ollama/ollama:latest
    ports:
      - "127.0.0.1:11434:11434"  # Localhost only
    volumes:
      - ollama_data:/root/.ollama
    deploy:
      resources:
        limits:
          memory: 32G
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: always
    logging:
      driver: json-file
      options:
        max-size: "10m"
        max-file: "3"

  chroma:
    image: chromadb/chroma:latest
    ports:
      - "127.0.0.1:8000:8000"  # Localhost only
    volumes:
      - chroma_data:/chroma/chroma
    environment:
      - CHROMA_SERVER_AUTHN_PROVIDER=chromadb.auth.token_authn.TokenAuthenticationServerProvider
      - CHROMA_SERVER_AUTHN_CREDENTIALS=${CHROMA_AUTH_TOKEN}
    restart: always

volumes:
  ollama_data:
  chroma_data:
```

---

## 9. Common Commands Reference

```bash
# Start services
docker compose up -d

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f ollama

# Stop services
docker compose down

# Stop and remove volumes (WARNING: deletes data!)
docker compose down -v

# Pull latest images
docker compose pull

# Restart specific service
docker compose restart ollama

# Execute command in container
docker exec -it ollama ollama list
docker exec -it ollama ollama pull llama3.2:3b

# Check resource usage
docker stats

# List volumes
docker volume ls

# Backup volume
docker run --rm -v ollama_data:/data -v $(pwd):/backup alpine tar czf /backup/ollama-backup.tar.gz -C /data .

# Restore volume
docker run --rm -v ollama_data:/data -v $(pwd):/backup alpine tar xzf /backup/ollama-backup.tar.gz -C /data
```

---

## 10. Troubleshooting Guide

### "GPU not detected" / Running on CPU
**Symptoms:** `ollama ps` shows "100% CPU"

**Fix (Windows with WSL2):**
1. Install NVIDIA drivers on Windows host
2. Install CUDA toolkit in WSL2
3. Enable GPU in Docker Desktop: Settings > Resources > WSL Integration > Enable GPU

**Fix (Linux):**
```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Models downloading every restart
**Cause:** Missing volume mount

**Fix:** Ensure volumes are properly defined in both service and top-level sections.

### Port conflicts
**Fix:** Change host port mapping:
```yaml
ports:
  - "11435:11434"  # Use 11435 on host instead of 11434
```

### Out of memory errors
**Fix:** Add memory limits and reduce parallel models:
```yaml
environment:
  - OLLAMA_MAX_LOADED_MODELS=1
deploy:
  resources:
    limits:
      memory: 16G
```

### Permission denied (Linux)
**Fix:**
```bash
sudo chown -R 1000:1000 ./data
```

---

## Conclusion and Recommendations

### For Our Specific Setup (OpenClaw on Windows)

**Option A: Native Installation (Recommended for simplicity)**
- Install Ollama natively on Windows
- Install ChromaDB via pip or run as needed
- OpenClaw connects via localhost
- **Pros:** Simpler, no Docker overhead, GPU works out of the box
- **Cons:** Manual setup for each service, harder to reproduce

**Option B: Docker for Services (Recommended for expansion)**
- Keep OpenClaw native on Windows
- Run Ollama + ChromaDB in Docker
- OpenClaw connects via exposed ports
- **Pros:** Easy to add services, reproducible, clean isolation
- **Cons:** Additional complexity, WSL2/Docker Desktop overhead

**Option C: Full Docker (Not recommended for OpenClaw)**
- Containerize everything including OpenClaw
- **Cons:** OpenClaw requires Windows integration that doesn't containerize well

### Final Recommendation

Start with **Option A** (native) for immediate needs. If we expand to include ChromaDB, WebUI, or other services, migrate to **Option B** (Docker for supporting services only).

The docker-compose.yml examples in this document can be used when we're ready to make that transition.

---

## Sources

1. [Local AI Development Stack with Docker Compose - MarkAICode](https://markaicode.com/docker-compose-local-ai-stack/)
2. [How to Run Chroma + Ollama in Docker - OneUptime](https://oneuptime.com/blog/post/2026-02-08-how-to-run-chroma-ollama-in-docker-for-local-ai-search/view)
3. [LLM Development Stack - Docker Recipes](https://docker.recipes/ai-ml/llm-development-stack)
4. [Ollama Models Setup with Docker Compose - Collabnix](https://collabnix.com/setting-up-ollama-models-with-docker-compose-a-step-by-step-guide/)
5. [Docker for Local AI Complete Guide - InsiderLLM](https://insiderllm.com/guides/docker-local-ai-ollama-open-webui-gpu-passthrough/)
6. [Self-hosted RAG with ChromaDB - Medium](https://medium.com/@mbrazel/open-source-self-hosted-rag-llm-server-with-chromadb-docker-ollama-7e6c6913da7a)
7. [AI Stack GitHub Repository](https://github.com/DmitryBoiadji/ai-stack)
8. [Docker Restart Policies - Docker Docs](https://docs.docker.com/engine/containers/start-containers-automatically/)
