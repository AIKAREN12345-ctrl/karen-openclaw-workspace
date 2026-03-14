# Docker Containerization for OpenClaw: A Complete Guide

**Research Date:** 2026-03-05  
**Purpose:** Understand how Docker can solve OpenClaw's localhost/sandbox isolation issues and improve system architecture

---

## Table of Contents

1. [What is Docker and How Does Containerization Work?](#1-what-is-docker-and-how-does-containerization-work)
2. [Docker Networking Deep Dive](#2-docker-networking-deep-dive)
3. [Solving OpenClaw's Localhost/Sandbox Isolation](#3-solving-openclaws-localhostsandbox-isolation)
4. [Docker Compose for Multi-Service Setups](#4-docker-compose-for-multi-service-setups)
5. [Resource Management and Limits](#5-resource-management-and-limits)
6. [Security Implications](#6-security-implications)
7. [Migration Path from Current Setup](#7-migration-path-from-current-setup)
8. [Practical Examples for OpenClaw](#8-practical-examples-for-openclaw)

---

## 1. What is Docker and How Does Containerization Work?

### The Analogy: Shipping Containers

Think of Docker like the shipping container revolution. Before standardized containers, loading a ship was chaotic—every item had different packaging, sizes, and handling requirements. Shipping containers standardized everything: no matter what's inside, the crane knows exactly how to lift it, the ship knows exactly where it fits, and the truck knows exactly how to transport it.

**Docker does the same for software.**

### What is Docker?

Docker is an open platform for developing, shipping, and running applications in **containers**. It enables you to separate your applications from your infrastructure so you can deliver software quickly and consistently.

### Key Concepts

#### Images
An **image** is a read-only template with instructions for creating a Docker container. Think of it as a blueprint or a snapshot of an application and all its dependencies.

```dockerfile
# Example: A simple Dockerfile (recipe for an image)
FROM python:3.10-alpine
WORKDIR /code
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

#### Containers
A **container** is a runnable instance of an image. It's a lightweight, isolated environment that includes:
- The application code
- Runtime (Python, Node.js, etc.)
- System tools
- System libraries
- Settings

**Key insight:** Containers share the host OS kernel but are isolated in their own process space, file system, and network stack.

### How Containerization Works (The Technical Bits)

Docker uses several Linux kernel features to provide isolation:

#### 1. Namespaces
Namespaces provide isolation by creating separate "views" of system resources:

| Namespace | What It Isolates |
|-----------|------------------|
| PID | Process IDs (processes in container can't see host processes) |
| NET | Network interfaces, routing tables, firewall rules |
| IPC | Inter-process communication (shared memory, message queues) |
| MNT | Mount points (file system hierarchy) |
| UTS | Hostname and domain name |
| USER | User and group IDs |

**Analogy:** Namespaces are like private offices in a building. Everyone works in the same building (kernel) but can't see into each other's offices.

#### 2. Control Groups (cgroups)
Cgroups limit and account for resource usage (CPU, memory, disk I/O, network). They ensure:
- No single container can exhaust system resources
- Fair resource sharing between containers
- Resource accounting and monitoring

#### 3. Union File Systems
Docker uses layered file systems (like OverlayFS) to:
- Share common base layers between containers
- Make containers lightweight (only store differences)
- Enable fast container startup

### Docker Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Docker Client                          │
│                    (docker CLI commands)                    │
└──────────────────────┬──────────────────────────────────────┘
                       │ REST API
┌──────────────────────▼──────────────────────────────────────┐
│                    Docker Daemon (dockerd)                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐  │
│  │   Images    │  │ Containers  │  │ Networks & Volumes  │  │
│  └─────────────┘  └─────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│              Host Operating System (Linux/Windows)          │
└─────────────────────────────────────────────────────────────┘
```

### Why Containers vs Virtual Machines?

| Feature | Virtual Machines | Docker Containers |
|---------|-----------------|-------------------|
| **Size** | GBs (full OS) | MBs (shared kernel) |
| **Startup** | Minutes | Seconds |
| **Performance** | Near native | Native (no hypervisor overhead) |
| **Isolation** | Strong (hardware-level) | Process-level |
| **Density** | Tens per host | Hundreds per host |

**The Bottom Line:** Containers are lighter, faster, and more efficient than VMs while providing sufficient isolation for most applications.

---

## 2. Docker Networking Deep Dive

### The Default Bridge Network

When Docker starts, it creates a default bridge network (`docker0` on Linux). Containers connected to this network:
- Get their own IP address (usually 172.17.0.x)
- Can communicate with each other using IP addresses
- Can reach external networks via NAT (Network Address Translation)
- Cannot be reached from outside without port mapping

```
┌─────────────────────────────────────────────────────────────┐
│                        Host Machine                         │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Docker Bridge Network                    │   │
│  │  ┌──────────────┐    ┌──────────────┐              │   │
│  │  │ Container A  │◄──►│ Container B  │              │   │
│  │  │ 172.17.0.2   │    │ 172.17.0.3   │              │   │
│  │  └──────────────┘    └──────────────┘              │   │
│  │           │                  │                      │   │
│  │           └──────────────────┘                      │   │
│  │                      │                              │   │
│  │              ┌───────▼────────┐                     │   │
│  │              │  docker0       │                     │   │
│  │              │  172.17.0.1    │                     │   │
│  │              └───────┬────────┘                     │   │
│  └──────────────────────┼──────────────────────────────┘   │
│                         │                                   │
│              ┌──────────▼──────────┐                       │
│              │   Host Network      │                       │
│              │   (Internet access) │                       │
│              └─────────────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

### Network Drivers

Docker supports multiple network drivers, each with different use cases:

#### 1. Bridge (Default)
- **Use case:** Most common, isolated internal networks
- **Behavior:** Containers on the same bridge can communicate; external access requires port mapping
- **Command:** `docker network create -d bridge my-network`

#### 2. Host
- **Use case:** When you need maximum network performance or need to avoid NAT
- **Behavior:** Container shares the host's network stack directly
- **Security:** Less isolation; container can bind to any host port
- **Command:** `docker run --network host my-app`

#### 3. None
- **Use case:** Completely isolated containers
- **Behavior:** No network interfaces except loopback
- **Command:** `docker run --network none my-app`

#### 4. Container
- **Use case:** Sidecar pattern, sharing network between containers
- **Behavior:** Container shares network namespace with another container
- **Command:** `docker run --network container:other-container my-app`

#### 5. Overlay
- **Use case:** Multi-host Docker Swarm clusters
- **Behavior:** Connects containers across different Docker hosts
- **Command:** `docker network create -d overlay my-overlay`

### User-Defined Networks (The Key to Service Discovery)

**This is crucial for OpenClaw.**

When you create a custom bridge network, Docker provides:
1. **Automatic DNS resolution:** Containers can reach each other by name
2. **Better isolation:** Only containers on the same network can communicate
3. **Custom IP ranges:** Configure subnets that don't conflict with your infrastructure

```yaml
# docker-compose.yml example
services:
  openclaw:
    image: openclaw:latest
    networks:
      - openclaw-network
  ollama:
    image: ollama/ollama
    networks:
      - openclaw-network

networks:
  openclaw-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

With this setup:
- OpenClaw can reach Ollama at `http://ollama:11434`
- Ollama can reach OpenClaw at `http://openclaw:8080`
- Both are isolated from other containers

### Port Publishing

To expose container ports to the outside world:

```bash
# Map host port 8080 to container port 80
docker run -p 8080:80 my-app

# Map to a random host port
docker run -p 80 my-app

# Map specific interface
docker run -p 127.0.0.1:8080:80 my-app
```

### DNS in Docker

- **Default bridge:** Uses host's DNS settings
- **Custom networks:** Uses Docker's embedded DNS server (at 127.0.0.11)
- **Container names:** Automatically resolve to container IPs on custom networks

---

## 3. Solving OpenClaw's Localhost/Sandbox Isolation

### The Current Problem

From TOOLS.md, we know:

> **Issue:** `local-automation` agent cannot use Ollama due to sandbox isolation
> - **Impact:** Cron jobs with `local-automation` + Ollama fail
> - **Workaround:** Use `agent:main` for Ollama tasks
> - **Status:** OpenClaw 2026.2.24 did not fix this

**What's happening:**
- OpenClaw subagents run in sandboxed environments
- They cannot access services running on `localhost` (like Ollama on port 11434)
- This is a security feature but creates architectural limitations

### How Docker Solves This

#### Solution 1: Shared Docker Network (Recommended)

Place both OpenClaw and Ollama in the same Docker network:

```yaml
# docker-compose.yml
services:
  openclaw:
    image: openclaw/openclaw:latest
    container_name: openclaw
    networks:
      - openclaw-internal
    environment:
      - OLLAMA_HOST=http://ollama:11434  # Use service name, not localhost
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    networks:
      - openclaw-internal
    volumes:
      - ollama-data:/root/.ollama
    # GPU support (Linux only)
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

networks:
  openclaw-internal:
    driver: bridge

volumes:
  ollama-data:
```

**Why this works:**
- Both services are on the same Docker network
- They can communicate using container names as hostnames
- No need for `localhost`—each service has its own network identity
- Sandboxed subagents can reach Ollama via `http://ollama:11434`

#### Solution 2: Host Network Mode (Simpler, Less Isolated)

```yaml
services:
  openclaw:
    image: openclaw/openclaw:latest
    network_mode: host  # Shares host network stack
    environment:
      - OLLAMA_HOST=http://localhost:11434
```

**Pros:**
- No port mapping needed
- Maximum performance
- Services see `localhost` the same way

**Cons:**
- No network isolation
- Port conflicts possible
- Less secure
- Not available on Docker Desktop for Mac/Windows (only Linux)

#### Solution 3: Expose Ollama to Host + Container Access

If Ollama runs on the host (not in Docker):

```yaml
services:
  openclaw:
    image: openclaw/openclaw:latest
    # On Linux, use host.docker.internal to reach host
    extra_hosts:
      - "host.docker.internal:host-gateway"
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
```

**Note:** On Windows/Mac Docker Desktop, `host.docker.internal` works automatically. On Linux, you need the `extra_hosts` configuration.

### The Complete Fix for OpenClaw

```yaml
# openclaw-stack.yml
version: "3.8"

services:
  # Main OpenClaw service
  openclaw:
    image: openclaw/openclaw:latest
    container_name: openclaw
    ports:
      - "18788:18788"  # Gateway port
      - "18800:18800"  # Browser CDP
    networks:
      - openclaw-net
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - NODE_ENV=production
    volumes:
      - openclaw-data:/data
      - openclaw-config:/config
    depends_on:
      - ollama
      - redis  # For caching/sessions
    restart: unless-stopped

  # Ollama for local LLM inference
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    networks:
      - openclaw-net
    volumes:
      - ollama-models:/root/.ollama
    # GPU support (Linux with nvidia-container-toolkit)
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

  # Optional: Redis for caching
  redis:
    image: redis:7-alpine
    container_name: openclaw-redis
    networks:
      - openclaw-net
    volumes:
      - redis-data:/data
    restart: unless-stopped

  # Optional: PostgreSQL for persistent storage
  postgres:
    image: postgres:16-alpine
    container_name: openclaw-postgres
    networks:
      - openclaw-net
    environment:
      - POSTGRES_USER=openclaw
      - POSTGRES_PASSWORD=${DB_PASSWORD:-changeme}
      - POSTGRES_DB=openclaw
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

networks:
  openclaw-net:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16

volumes:
  openclaw-data:
  openclaw-config:
  ollama-models:
  redis-data:
  postgres-data:
```

**Usage:**
```bash
# Start everything
docker compose -f openclaw-stack.yml up -d

# View logs
docker compose -f openclaw-stack.yml logs -f

# Stop everything
docker compose -f openclaw-stack.yml down

# Update
docker compose -f openclaw-stack.yml pull
docker compose -f openclaw-stack.yml up -d
```

---

## 4. Docker Compose for Multi-Service Setups

### What is Docker Compose?

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you:
- Define your entire application stack in a YAML file
- Start all services with a single command
- Ensure services start in the correct order
- Manage networks and volumes automatically

### Key Compose Concepts

#### Services
Each container you want to run is defined as a service:

```yaml
services:
  web:
    image: nginx:latest
    ports:
      - "80:80"
  
  database:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
```

#### Networks
Compose creates a default network, but you can define custom ones:

```yaml
services:
  app:
    networks:
      - frontend
      - backend
  
  db:
    networks:
      - backend

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
```

#### Volumes
Persistent data storage:

```yaml
services:
  db:
    volumes:
      - db-data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

volumes:
  db-data:
```

### Docker Compose Commands

| Command | Description |
|---------|-------------|
| `docker compose up` | Create and start containers |
| `docker compose up -d` | Start in detached mode (background) |
| `docker compose down` | Stop and remove containers |
| `docker compose down -v` | Stop and remove containers + volumes |
| `docker compose ps` | List running containers |
| `docker compose logs` | View container logs |
| `docker compose logs -f` | Follow log output |
| `docker compose exec <service> <cmd>` | Run command in container |
| `docker compose build` | Build or rebuild services |
| `docker compose pull` | Pull latest images |

### Compose File Versions

- **Version 3.x:** Recommended for new projects
- **Version 2.x:** Legacy, still supported
- Use `version: "3.8"` for modern features

### Environment Variables in Compose

```yaml
services:
  app:
    environment:
      - DATABASE_URL=postgres://user:pass@db:5432/mydb
      - DEBUG=${DEBUG:-false}  # Default to false if not set
    env_file:
      - .env  # Load from file
```

---

## 5. Resource Management and Limits

### Why Resource Limits Matter

Without limits, a single container can:
- Consume all available memory, causing OOM (Out of Memory) kills
- Starve other containers of CPU
- Exhaust disk space with logs
- Impact overall system stability

### Memory Limits

```bash
# Hard limit: container cannot exceed 512MB
docker run -m 512m my-app

# Hard limit with swap (total memory + swap = 1GB)
docker run -m 512m --memory-swap 1g my-app

# No swap allowed
docker run -m 512m --memory-swap 512m my-app
```

**In Compose:**
```yaml
services:
  app:
    image: my-app
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M
```

### CPU Limits

```bash
# Limit to 1.5 CPUs
docker run --cpus="1.5" my-app

# Limit to specific cores
docker run --cpuset-cpus="0,1" my-app

# CPU shares (relative weight, default 1024)
docker run --cpu-shares=512 my-app  # Half the priority
```

**In Compose:**
```yaml
services:
  app:
    deploy:
      resources:
        limits:
          cpus: '1.5'
        reservations:
          cpus: '0.5'
```

### GPU Access

For Ollama with GPU acceleration (Linux only):

```bash
# All GPUs
docker run --gpus all ollama/ollama

# Specific GPU
docker run --gpus '"device=0"' ollama/ollama

# Multiple GPUs
docker run --gpus '"device=0,2"' ollama/ollama
```

**In Compose:**
```yaml
services:
  ollama:
    image: ollama/ollama
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

**Prerequisites for GPU:**
1. Install NVIDIA drivers on host
2. Install nvidia-container-toolkit
3. Restart Docker daemon

### Disk I/O Limits

```bash
# Limit read/write speed
docker run --device-read-bps /dev/sda:1mb --device-write-bps /dev/sda:1mb my-app
```

### OpenClaw Resource Recommendations

Based on the current system (Windows 11, local LLMs):

```yaml
services:
  openclaw:
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
        reservations:
          memory: 512M
          cpus: '0.5'

  ollama:
    deploy:
      resources:
        limits:
          memory: 12G  # Adjust based on your largest model
          cpus: '4.0'
        reservations:
          memory: 4G
          cpus: '2.0'
```

---

## 6. Security Implications

### Docker Security Model

Docker provides isolation through:
1. **Kernel namespaces** (process, network, mount isolation)
2. **Control groups** (resource limits)
3. **Capabilities** (fine-grained privilege control)
4. **Seccomp** (syscall filtering)
5. **AppArmor/SELinux** (mandatory access control)

### Security: Docker vs Current Setup

| Aspect | Current OpenClaw | Dockerized OpenClaw |
|--------|------------------|---------------------|
| **Process isolation** | Sandboxed subagents | Container namespaces |
| **Network isolation** | Limited | Configurable per-container |
| **Resource limits** | Limited | Full cgroup support |
| **Filesystem isolation** | Partial | Full container filesystem |
| **Privilege escalation** | Risk if sandbox breaks | Root in container ≠ root on host |
| **Attack surface** | OpenClaw sandbox code | Docker daemon + kernel |

### Security Best Practices

#### 1. Run as Non-Root User

```dockerfile
# Dockerfile
FROM node:18-alpine
# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
# Switch to non-root user
USER nextjs
```

#### 2. Use Minimal Base Images

```dockerfile
# Bad: Full Ubuntu image
FROM ubuntu:22.04

# Good: Alpine Linux (5MB vs 80MB)
FROM alpine:latest

# Better: Distroless (Google's minimal images)
FROM gcr.io/distroless/nodejs18-debian11
```

#### 3. Read-Only Filesystems

```bash
docker run --read-only my-app
```

**In Compose:**
```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
      - /var/cache
```

#### 4. Drop Unnecessary Capabilities

```bash
docker run --cap-drop=ALL --cap-add=NET_BIND_SERVICE my-app
```

#### 5. Security Scanning

```bash
# Scan image for vulnerabilities
docker scan my-image

# Or use Trivy
trivy image my-image
```

#### 6. Content Trust

```bash
# Only run signed images
export DOCKER_CONTENT_TRUST=1
docker pull official-image
```

### Rootless Docker

For maximum security, run Docker daemon as non-root:

```bash
# Install rootless Docker
curl -fsSL https://get.docker.com/rootless | sh

# Start daemon
dockerd-rootless-setuptool.sh install
```

**Benefits:**
- Daemon runs as unprivileged user
- Container root is mapped to non-root on host
- Even container escape doesn't grant root access

### OpenClaw Security Considerations

**Current risks:**
- Subagents can potentially escape sandbox
- Direct access to host filesystem
- Network access to localhost services

**Docker mitigations:**
```yaml
services:
  openclaw:
    # Run as non-root
    user: "1000:1000"
    
    # Read-only root filesystem
    read_only: true
    
    # Limit capabilities
    cap_drop:
      - ALL
    cap_add:
      - CHOWN
      - SETGID
      - SETUID
    
    # No new privileges
    security_opt:
      - no-new-privileges:true
    
    # Resource limits
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'
    
    # Network isolation
    networks:
      - openclaw-internal
    
    # Limited filesystem access
    volumes:
      - type: bind
        source: ./data
        target: /data
        read_only: false
      - type: bind
        source: ./config
        target: /config
        read_only: true
```

---

## 7. Migration Path from Current Setup

### Phase 1: Assessment (Week 1)

1. **Inventory current services:**
   - OpenClaw gateway (port 18788)
   - Browser CDP (port 18800)
   - Ollama (port 11434)
   - Any databases or caches

2. **Identify dependencies:**
   - Node.js version
   - Python version (for subagents)
   - System libraries
   - Configuration files

3. **Document data locations:**
   - `~/.openclaw/`
   - `~/.ollama/`
   - Any custom scripts

### Phase 2: Containerize Individual Services (Week 2-3)

#### Step 1: Create OpenClaw Dockerfile

```dockerfile
# Dockerfile.openclaw
FROM node:20-alpine

# Install dependencies
RUN apk add --no-cache \
    python3 \
    py3-pip \
    git \
    curl

# Create app directory
WORKDIR /app

# Copy package files
COPY package*.json ./
RUN npm ci --only=production

# Copy application
COPY . .

# Create non-root user
RUN addgroup -g 1001 -S openclaw && \
    adduser -S openclaw -u 1001

# Set permissions
RUN chown -R openclaw:openclaw /app
USER openclaw

# Expose ports
EXPOSE 18788 18800

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:18788/health || exit 1

# Start command
CMD ["node", "dist/gateway.js"]
```

#### Step 2: Test Ollama Container

```bash
# Pull and test Ollama
docker pull ollama/ollama:latest

# Run with volume for models
docker run -d \
  -v ollama-models:/root/.ollama \
  -p 11434:11434 \
  --name ollama \
  ollama/ollama:latest

# Test
docker exec -it ollama ollama run llama2
```

#### Step 3: Create docker-compose.yml

```yaml
version: "3.8"

services:
  openclaw:
    build:
      context: .
      dockerfile: Dockerfile.openclaw
    ports:
      - "18788:18788"
      - "18800:18800"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - NODE_ENV=production
    volumes:
      - openclaw-data:/app/data
      - ./config:/app/config:ro
    networks:
      - openclaw-net
    depends_on:
      - ollama
    restart: unless-stopped

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama-models:/root/.ollama
    networks:
      - openclaw-net
    restart: unless-stopped

networks:
  openclaw-net:
    driver: bridge

volumes:
  openclaw-data:
  ollama-models:
```

### Phase 3: Data Migration (Week 4)

1. **Backup existing data:**
   ```bash
   # Backup Ollama models
   tar -czf ollama-backup.tar.gz ~/.ollama/
   
   # Backup OpenClaw config
   tar -czf openclaw-backup.tar.gz ~/.openclaw/
   ```

2. **Import to Docker volumes:**
   ```bash
   # Create volume and extract
   docker volume create ollama-models
   docker run --rm \
     -v ollama-models:/target \
     -v ~/ollama-backup.tar.gz:/backup.tar.gz \
     alpine tar -xzf /backup.tar.gz -C /target
   ```

### Phase 4: Testing (Week 5)

1. **Functional testing:**
   - Start stack: `docker compose up -d`
   - Test OpenClaw gateway
   - Test Ollama connectivity
   - Run sample subagent tasks

2. **Performance testing:**
   - Compare response times
   - Monitor resource usage
   - Test under load

3. **Failover testing:**
   - Restart individual containers
   - Test persistence
   - Verify data integrity

### Phase 5: Cutover (Week 6)

1. **Stop native services:**
   ```bash
   # Stop native Ollama
   # Stop native OpenClaw
   ```

2. **Start Docker stack:**
   ```bash
   docker compose up -d
   ```

3. **Verification:**
   - All services healthy
   - Data intact
   - Performance acceptable

### Rollback Plan

If issues occur:

```bash
# Stop Docker
docker compose down

# Restore native services
# Restore from backups if needed
```

---

## 8. Practical Examples for OpenClaw

### Example 1: Basic OpenClaw + Ollama Setup

```yaml
# basic-setup.yml
version: "3.8"

services:
  openclaw:
    image: openclaw/openclaw:latest
    ports:
      - "18788:18788"
    environment:
      - OLLAMA_HOST=http://ollama:11434
    networks:
      - openclaw
    depends_on:
      - ollama

  ollama:
    image: ollama/ollama:latest
    networks:
      - openclaw
    volumes:
      - ollama-data:/root/.ollama

networks:
  openclaw:

volumes:
  ollama-data:
```

**Run:**
```bash
docker compose -f basic-setup.yml up -d
```

### Example 2: Development Environment with Hot Reload

```yaml
# dev-setup.yml
version: "3.8"

services:
  openclaw:
    build:
      context: .
      dockerfile: Dockerfile.dev
    ports:
      - "18788:18788"
      - "18800:18800"
    environment:
      - NODE_ENV=development
      - OLLAMA_HOST=http://ollama:11434
    volumes:
      - .:/app
      - /app/node_modules
    networks:
      - openclaw
    command: npm run dev

  ollama:
    image: ollama/ollama:latest
    networks:
      - openclaw
    volumes:
      - ollama-data:/root/.ollama

networks:
  openclaw:

volumes:
  ollama-data:
```

### Example 3: Production Stack with All Services

```yaml
# production-stack.yml
version: "3.8"

services:
  # Reverse proxy
  traefik:
    image: traefik:v3.0
    command:
      - "--api.insecure=true"
      - "--providers.docker=true"
      - "--providers.docker.exposedbydefault=false"
      - "--entrypoints.web.address=:80"
      - "--entrypoints.websecure.address=:443"
    ports:
      - "80:80"
      - "443:443"
      - "8080:8080"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
    networks:
      - openclaw

  # OpenClaw
  openclaw:
    image: openclaw/openclaw:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.openclaw.rule=Host(`openclaw.local`)"
      - "traefik.http.services.openclaw.loadbalancer.server.port=18788"
    environment:
      - OLLAMA_HOST=http://ollama:11434
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgres://openclaw:${DB_PASSWORD}@postgres:5432/openclaw
    networks:
      - openclaw
    depends_on:
      - ollama
      - redis
      - postgres
    deploy:
      resources:
        limits:
          memory: 2G
          cpus: '2.0'

  # Ollama
  ollama:
    image: ollama/ollama:latest
    networks:
      - openclaw
    volumes:
      - ollama-data:/root/.ollama
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '4.0'
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]

  # Redis
  redis:
    image: redis:7-alpine
    networks:
      - openclaw
    volumes:
      - redis-data:/data
    command: redis-server --appendonly yes

  # PostgreSQL
  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=openclaw
      - POSTGRES_PASSWORD=${DB_PASSWORD}
      - POSTGRES_DB=openclaw
    networks:
      - openclaw
    volumes:
      - postgres-data:/var/lib/postgresql/data

networks:
  openclaw:
    driver: bridge

volumes:
  ollama-data:
  redis-data:
  postgres-data:
```

### Example 4: Windows-Specific Setup

Since the current system is Windows 11:

```yaml
# windows-setup.yml
version: "3.8"

services:
  openclaw:
    image: openclaw/openclaw:latest
    ports:
      - "18788:18788"
      - "18800:18800"
    environment:
      # On Windows Docker Desktop, use host.docker.internal to reach host
      - OLLAMA_HOST=http://host.docker.internal:11434
    volumes:
      # Windows path syntax
      - C:\openclaw\data:/app/data
      - C:\openclaw\config:/app/config:ro
    extra_hosts:
      - "host.docker.internal:host-gateway"

  # Note: Ollama runs on host (Windows) for GPU access
  # Docker Desktop on Windows doesn't support GPU passthrough for Linux containers
```

**Alternative:** Run Ollama in WSL2 with Docker:

```bash
# In WSL2 Ubuntu
sudo apt update
sudo apt install docker.io

# Run Ollama container with GPU
docker run -d --gpus all -v ollama:/root/.ollama -p 11434:11434 ollama/ollama

# OpenClaw in Docker Desktop can reach it via host IP
```

### Example 5: Troubleshooting Container Issues

```bash
# Check container logs
docker logs openclaw

# Follow logs in real-time
docker logs -f openclaw

# Execute shell in container
docker exec -it openclaw /bin/sh

# Check network connectivity
docker exec -it openclaw ping ollama

# Inspect container details
docker inspect openclaw

# Check resource usage
docker stats

# Restart a service
docker compose restart ollama
```

---

## Summary: Key Takeaways for OpenClaw

### The Problem Docker Solves

OpenClaw's current architecture has a critical limitation: **subagents running in sandboxes cannot access services on localhost** (like Ollama). This prevents automated tasks from using local LLMs.

### The Docker Solution

By containerizing both OpenClaw and Ollama:
1. They share a private Docker network
2. They communicate via container names (DNS), not localhost
3. Subagents can reach Ollama at `http://ollama:11434`
4. The sandbox isolation issue is eliminated

### Recommended Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Docker Network: openclaw                      │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   OpenClaw   │◄────►│    Ollama    │◄────►│    Redis     │  │
│  │   :18788     │      │   :11434     │      │   :6379      │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                                                       │
│         │ Exposed to host                                       │
└─────────┼───────────────────────────────────────────────────────┘
          │
    ┌─────▼──────┐
    │   Host     │
    │  (Windows) │
    └────────────┘
```

### Next Steps

1. **Install Docker Desktop** on Windows 11
2. **Create a docker-compose.yml** with OpenClaw + Ollama
3. **Test connectivity** between services
4. **Migrate existing data** (models, configs)
5. **Update subagent configurations** to use `http://ollama:11434`
6. **Validate** that sandboxed subagents can now access Ollama

### Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/compose-file/)
- [Ollama Docker Image](https://hub.docker.com/r/ollama/ollama)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)

---

*Document created for OpenClaw research. Assumes reader has no prior Docker experience.*
