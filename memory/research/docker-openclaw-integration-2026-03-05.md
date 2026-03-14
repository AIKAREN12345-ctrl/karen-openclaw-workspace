# Docker Solutions for OpenClaw and Local LLM Integration

**Research Date:** 2026-03-05  
**Focus:** Solving the cron job + Ollama sandbox isolation problem with Docker containerization

---

## Executive Summary

This research explores Docker-based solutions to address the core problem: **OpenClaw's `local-automation` agent cannot access Ollama due to sandbox isolation**. The investigation covers OpenClaw Docker setup, Ollama containerization with GPU support, shared networking strategies, volume persistence, and performance comparisons between Docker and native installations.

**Key Finding:** Docker Compose with shared custom networks and named volumes offers a viable solution for co-locating OpenClaw and Ollama containers, enabling seamless inter-container communication while maintaining data persistence.

---

## 1. OpenClaw Docker Setup and Configuration

### 1.1 Official Docker Support

OpenClaw provides official Docker support through multiple channels:

- **Documentation:** https://docs.openclaw.ai/install/docker
- **Pre-built Images:** `ghcr.io/openclaw/openclaw:latest` (GitHub Container Registry)
- **Setup Script:** `docker-setup.sh` for automated configuration

### 1.2 Containerized Gateway Architecture

OpenClaw supports two Docker deployment modes:

1. **Containerized Gateway** - Full OpenClaw running entirely in Docker
2. **Per-session Agent Sandbox** - Host gateway with Docker-isolated agent tools

### 1.3 Key Configuration Options

| Environment Variable | Purpose |
|---------------------|---------|
| `OPENCLAW_IMAGE` | Use remote image (e.g., `ghcr.io/openclaw/openclaw:latest`) |
| `OPENCLAW_SANDBOX=1` | Enable Docker gateway sandbox bootstrap |
| `OPENCLAW_EXTRA_MOUNTS` | Add extra host bind mounts (comma-separated) |
| `OPENCLAW_HOME_VOLUME` | Persist `/home/node` in a named volume |
| `OPENCLAW_DOCKER_APT_PACKAGES` | Install extra packages during build |
| `OPENCLAW_DOCKER_SOCKET` | Override Docker socket path |

### 1.4 Quick Start (Docker Compose)

```bash
# Using official setup script
export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
./docker-setup.sh

# Manual compose flow
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm openclaw-cli onboard
docker compose up -d openclaw-gateway
```

### 1.5 Shared Network Security Model

The `openclaw-cli` service uses `network_mode: "service:openclaw-gateway"` enabling CLI commands to reach the gateway over `127.0.0.1`. This creates a shared trust boundary between containers.

---

## 2. Running Ollama in Docker with GPU Support

### 2.1 Official Ollama Docker Image

Ollama is available as an official Docker sponsored open-source image:
- **Docker Hub:** `ollama/ollama`
- **GitHub:** https://github.com/ollama/ollama

### 2.2 Platform-Specific GPU Support

#### Linux (Full GPU Support)
```bash
# CPU only
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# NVIDIA GPU (requires NVIDIA Container Toolkit)
docker run -d --gpus=all -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama

# AMD GPU (ROCm)
docker run -d --device /dev/kfd --device /dev/dri -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama:rocm
```

#### macOS
**Important:** Docker Desktop on Mac does NOT support GPU passthrough. Ollama recommends running as a standalone application outside Docker on Mac.

#### Windows (WSL2 + GPU-PV)
Docker Desktop for Windows supports NVIDIA GPU Paravirtualization (GPU-PV) on WSL2:

**Prerequisites:**
- Windows 10/11 with up-to-date NVIDIA drivers supporting WSL2 GPU-PV
- Latest WSL2 Linux kernel (`wsl --update`)
- WSL2 backend enabled in Docker Desktop

**Validation:**
```bash
docker run --rm -it --gpus=all nvcr.io/nvidia/k8s/cuda-sample:nbody nbody -gpu -benchmark
```

### 2.3 NVIDIA Container Toolkit Installation

**Ubuntu/Debian:**
```bash
# Configure repository
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# Install
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

---

## 3. Shared Networking Between OpenClaw and Ollama Containers

### 3.1 Docker Compose Default Networking

By default, Docker Compose creates a single network where all service containers can communicate using service names as hostnames.

```yaml
services:
  openclaw-gateway:
    image: ghcr.io/openclaw/openclaw:latest
    # ... other config
    
  ollama:
    image: ollama/ollama:latest
    # OpenClaw can reach Ollama at http://ollama:11434
```

### 3.2 Custom Network Configuration

For explicit control, define a custom network:

```yaml
services:
  openclaw:
    image: ghcr.io/openclaw/openclaw:latest
    networks:
      - openclaw-network
    environment:
      - OLLAMA_HOST=http://ollama:11434
      
  ollama:
    image: ollama/ollama:latest
    networks:
      - openclaw-network
    volumes:
      - ollama-data:/root/.ollama

networks:
  openclaw-network:
    driver: bridge
    
volumes:
  ollama-data:
```

### 3.3 Real-World Example: Open WebUI + Ollama

The Open WebUI project demonstrates this pattern:

```yaml
services:
  ollama:
    volumes:
      - ollama:/root/.ollama
    container_name: ollama
    pull_policy: always
    tty: true
    restart: unless-stopped
    image: ollama/ollama:${OLLAMA_DOCKER_TAG-latest}

  open-webui:
    build:
      context: .
      dockerfile: Dockerfile
    image: ghcr.io/open-webui/open-webui:${WEBUI_DOCKER_TAG-main}
    container_name: open-webui
    volumes:
      - open-webui:/app/backend/data
    depends_on:
      - ollama
    ports:
      - ${OPEN_WEBUI_PORT-3000}:8080
    environment:
      - 'OLLAMA_BASE_URL=http://ollama:11434'
    extra_hosts:
      - host.docker.internal:host-gateway
    restart: unless-stopped

volumes:
  ollama: {}
  open-webui: {}
```

### 3.4 Network Mode Alternatives

| Mode | Use Case | Example |
|------|----------|---------|
| `bridge` (default) | Standard inter-container communication | Most setups |
| `host` | Direct host network access (Linux only) | Performance-critical |
| `service:name` | Share network namespace | OpenClaw CLI + Gateway |
| `container:name` | Share another container's network | Legacy compatibility |

---

## 4. Volume Mounts for Persistent Data

### 4.1 Named Volumes vs Bind Mounts

| Type | Use Case | Persistence |
|------|----------|-------------|
| **Named Volumes** | Data managed by Docker, portable | Survives container recreation |
| **Bind Mounts** | Direct host filesystem access | Host path dependent |
| **tmpfs** | Ephemeral, high-performance data | Lost on container stop |

### 4.2 Ollama Data Persistence

Ollama stores models and data in `/root/.ollama`:

```yaml
volumes:
  # Named volume approach (recommended)
  ollama-data:
    driver: local

services:
  ollama:
    volumes:
      - ollama-data:/root/.ollama
```

### 4.3 OpenClaw Data Persistence

OpenClaw uses several paths that should persist:

```yaml
volumes:
  openclaw-home:  # /home/node for user data
  openclaw-config:  # ~/.openclaw configuration
  openclaw-workspace:  # Workspace files

services:
  openclaw:
    volumes:
      - openclaw-home:/home/node
      - openclaw-config:/home/node/.openclaw
      - openclaw-workspace:/home/node/.openclaw/workspace
```

### 4.4 Volume Backup and Migration

```bash
# Backup volume
docker run --rm --volumes-from ollama -v $(pwd):/backup ubuntu tar cvf /backup/ollama-backup.tar /root/.ollama

# Restore to new volume
docker volume create ollama-new
docker run --rm -v ollama-new:/root/.ollama -v $(pwd):/backup ubuntu bash -c "cd /root/.ollama && tar xvf /backup/ollama-backup.tar --strip 1"
```

---

## 5. Docker Alternatives to Localhost Access Problem

### 5.1 The Core Problem

OpenClaw's `local-automation` agent runs in a sandbox that cannot access host services (like Ollama on `localhost:11434`). This is by design for security but breaks local LLM integration.

### 5.2 Solution: Container Co-location

**Architecture:** Run both OpenClaw and Ollama in the same Docker Compose network.

```yaml
version: '3.8'

services:
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama-data:/root/.ollama
    networks:
      - ai-network
    # GPU support for Linux/WSL2
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

  openclaw-gateway:
    image: ghcr.io/openclaw/openclaw:latest
    container_name: openclaw
    environment:
      # Point to Ollama service name, not localhost
      - OLLAMA_BASE_URL=http://ollama:11434
      - DEFAULT_MODEL=qwen2.5:14b
    volumes:
      - openclaw-home:/home/node
      - openclaw-data:/home/node/.openclaw
      # Mount workspace for persistent files
      - ${USERPROFILE}/.openclaw/workspace:/home/node/.openclaw/workspace
    networks:
      - ai-network
    ports:
      - "18789:18789"  # OpenClaw web UI
    depends_on:
      - ollama
    restart: unless-stopped

  # Optional: Pre-load models
  ollama-pull:
    image: ollama/ollama:latest
    container_name: ollama-pull
    entrypoint: >
      sh -c "
        sleep 10 &&
        ollama pull qwen2.5:14b &&
        ollama pull nomic-embed-text
      "
    networks:
      - ai-network
    depends_on:
      - ollama
    restart: "no"

networks:
  ai-network:
    driver: bridge

volumes:
  ollama-data:
  openclaw-home:
  openclaw-data:
```

### 5.3 Alternative: Host Network Mode (Linux Only)

For maximum performance on Linux hosts:

```yaml
services:
  ollama:
    image: ollama/ollama:latest
    network_mode: host  # Shares host network namespace
    # ... other config
```

**Warning:** Not available on Docker Desktop for Windows/Mac.

### 5.4 Alternative: Docker-in-Docker (DinD)

For complete isolation with nested container support:

```yaml
services:
  openclaw-dind:
    image: docker:dind
    privileged: true
    volumes:
      - openclaw-data:/var/lib/docker
```

---

## 6. Real-World AI/LLM Docker Setups

### 6.1 Open WebUI + Ollama Stack

**GitHub:** https://github.com/open-webui/open-webui

A complete web interface for Ollama with Docker Compose:
- Ollama container for model serving
- Open WebUI container for chat interface
- Shared network for internal communication
- Named volumes for model and data persistence

### 6.2 LangChain + Ollama Integration

```yaml
services:
  langchain-app:
    build: ./app
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
```

### 6.3 Multi-Model Setup

```yaml
services:
  ollama-primary:
    image: ollama/ollama:latest
    volumes:
      - ollama-primary:/root/.ollama
    ports:
      - "11434:11434"

  ollama-secondary:
    image: ollama/ollama:latest
    volumes:
      - ollama-secondary:/root/.ollama
    ports:
      - "11435:11434"
```

---

## 7. Performance Comparison: Docker vs Native

### 7.1 General Performance Characteristics

| Aspect | Native | Docker | Notes |
|--------|--------|--------|-------|
| **Startup Time** | Fast | Slightly slower | Container initialization overhead |
| **Memory Usage** | Baseline | +10-15% overhead | Container runtime overhead |
| **CPU Performance** | 100% | ~98-99% | Negligible overhead |
| **GPU Performance** | 100% | ~95-98% | NVIDIA Container Toolkit overhead |
| **I/O Performance** | 100% | ~90-95% | Volume/driver overhead |
| **Network (local)** | 100% | ~95-98% | Bridge network overhead |

### 7.2 LLM-Specific Considerations

**Model Loading:**
- Native: Direct memory mapping from disk
- Docker: Volume-mounted files may have slight I/O overhead
- Impact: Minimal for SSDs, noticeable for large models on HDDs

**Inference Speed:**
- GPU: Near-native performance with `--gpus=all`
- CPU: Slight overhead from containerization
- Quantized models: Negligible difference

**Memory Management:**
- Native: Direct OS memory management
- Docker: Additional cgroup accounting overhead
- WSL2 on Windows: Dynamic memory allocation can cause initial latency

### 7.3 Windows-Specific Considerations

**WSL2 Backend:**
- Uses lightweight VM with full Linux kernel
- File system performance: Improved with WSL2 vs WSL1
- GPU support: Available via GPU-PV (Paravirtualization)
- Memory: Dynamic allocation prevents host memory starvation

**Potential Issues:**
- Windows Defender Firewall may block WSL2 network access
- Solution: Configure firewall rules for WSL2 vEthernet adapter

### 7.4 When to Use Docker vs Native

**Use Docker when:**
- Need isolated, reproducible environments
- Running multiple AI services that need networking
- Sharing setups across teams/machines
- Running on VPS/cloud without local installs
- Need easy rollback/version management

**Use Native when:**
- Maximum performance is critical
- Running on macOS (no GPU support in Docker)
- Simple single-service deployment
- Development loop requires fastest iteration

---

## 8. Recommended Implementation for OpenClaw + Ollama

### 8.1 Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Docker Compose Network                    │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  OpenClaw        │◄──────►│  Ollama          │          │
│  │  Gateway         │  HTTP  │  LLM Server      │          │
│  │                  │        │  Port 11434      │          │
│  └──────────────────┘        └──────────────────┘          │
│         │                             │                     │
│         ▼                             ▼                     │
│  ┌──────────────────┐        ┌──────────────────┐          │
│  │  Named Volume    │        │  Named Volume    │          │
│  │  openclaw-data   │        │  ollama-data     │          │
│  └──────────────────┘        └──────────────────┘          │
└─────────────────────────────────────────────────────────────┘
```

### 8.2 Implementation Steps

1. **Install Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
2. **Enable WSL2** (Windows) for better performance
3. **Install NVIDIA Container Toolkit** (if using GPU on Linux)
4. **Create `docker-compose.yml`** with both services
5. **Configure OpenClaw** to use `http://ollama:11434` as Ollama host
6. **Start services** with `docker compose up -d`
7. **Verify connectivity** from OpenClaw container to Ollama

### 8.3 Configuration for OpenClaw

In OpenClaw configuration, update the Ollama provider:

```json
{
  "providers": {
    "ollama": {
      "baseUrl": "http://ollama:11434",
      "defaultModel": "qwen2.5:14b"
    }
  }
}
```

---

## 9. References and Sources

1. **OpenClaw Docker Documentation:** https://docs.openclaw.ai/install/docker
2. **Ollama Docker Hub:** https://hub.docker.com/r/ollama/ollama
3. **Ollama Docker Announcement:** https://ollama.com/blog/ollama-is-now-available-as-an-official-docker-image
4. **NVIDIA Container Toolkit:** https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html
5. **Docker Compose Networking:** https://docs.docker.com/compose/how-tos/networking/
6. **Docker Volumes:** https://docs.docker.com/engine/storage/volumes/
7. **Docker Desktop WSL2:** https://docs.docker.com/desktop/features/wsl/
8. **Docker Desktop GPU Support:** https://docs.docker.com/desktop/features/gpu/
9. **Open WebUI Docker Compose:** https://github.com/open-webui/open-webui

---

## 10. Next Steps

1. **Test the proposed Docker Compose configuration** on the target system
2. **Verify GPU passthrough** works correctly (if applicable)
3. **Benchmark performance** against native installation
4. **Document any Windows-specific firewall** or networking adjustments needed
5. **Consider creating a custom OpenClaw image** with pre-configured Ollama integration

---

*This research document addresses the specific problem of OpenClaw's sandboxed agents being unable to reach Ollama on localhost. The Docker Compose co-location approach provides a clean solution while maintaining data persistence and enabling GPU acceleration where supported.*
