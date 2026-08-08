# Research: OpenClaw Docker Migration on Windows 11 (2026)

**Date:** 2026-04-13  
**Researcher:** Karen (subagent)  
**Focus:** Evaluating whether migrating OpenClaw to Docker Desktop on Windows 11 is worthwhile

---

## 1. Current State of Docker Desktop on Windows (2026)

### GPU Passthrough
- **Status:** ✅ Fully supported via WSL2 backend
- **Requirements:** 
  - NVIDIA GPU with WSL2-compatible drivers (535+ minimum, 560+ recommended)
  - Windows 11 (or Windows 10 with WSL2)
  - Docker Desktop with WSL2 backend enabled
- **Implementation:** Uses NVIDIA GPU Paravirtualization (GPU-PV)
- **Performance:** ~95-100% of native Linux performance for GPU-bound inference
- **Verification:** `docker run --rm --gpus=all nvidia/cuda:12.6.0-runtime-ubuntu24.04 nvidia-smi`

### WSL2 Integration
- **Default Backend:** Docker Desktop on Windows uses WSL2 as its backend (not Hyper-V by default)
- **Architecture:** Windows Host → Hyper-V → WSL2 VM → Docker Engine → Containers
- **File System Performance:** 
  - WSL2 native filesystem: Fast
  - `/mnt/c/` (Windows drives): 3-5x slower
  - **Recommendation:** Keep project files inside WSL2 filesystem
- **Networking:**
  - `networkingMode=mirrored` (Windows 11 22H2+): Shares host network stack, includes VPN
  - Default NAT mode: Requires port forwarding for external access

### Performance Characteristics
- **Startup:** ~3-10 seconds to exit Resource Saver mode on Windows
- **GPU Inference:** Negligible overhead vs native (<5% difference)
- **CPU Inference:** Linux native is consistently faster

---

## 2. Pros and Cons for OpenClaw + Ollama in Docker

### ✅ Pros

| Benefit | Details |
|---------|---------|
| **Isolation** | OpenClaw runs code, browses web, executes shell commands - Docker contains all of this |
| **Reproducibility** | Pin an image tag, get identical environment months later |
| **Clean Uninstall** | Remove containers + volumes = completely gone, no leftover packages |
| **Multi-service** | Docker Compose makes running OpenClaw + Ollama + monitoring trivial |
| **VPS Deployment** | Same setup works on Hetzner, DigitalOcean, AWS - standardized environment |
| **Sandbox Mode** | OpenClaw can create separate Docker containers per agent session for stronger isolation |
| **Pre-built Images** | Official GHCR images available: `ghcr.io/openclaw/openclaw:latest` |

### ❌ Cons

| Drawback | Details |
|----------|---------|
| **Resource Overhead** | ~100-200MB extra RAM vs native |
| **Build Requirements** | 2GB+ RAM needed for build phase (can use pre-built images to skip) |
| **WSL2 Complexity** | Another layer to manage and troubleshoot |
| **File System** | Must keep data in WSL2 filesystem for performance |
| **VPN Issues** | Corporate VPNs (Cisco AnyConnect, GlobalProtect) commonly break WSL2 networking |
| **Disk Bloat** | WSL2 VHDX grows but doesn't shrink automatically (mitigated with `sparseVhd=true`) |

### Comparison: Docker vs Native for OpenClaw

| Factor | Docker | Native Windows |
|--------|--------|----------------|
| Setup Time | 5-10 min | 3-5 min |
| Isolation | Full container isolation | Runs on host directly |
| Updates | Pull new image, restart | `git pull`, rebuild |
| Resource Overhead | ~100-200 MB extra | None |
| Cleanup | Remove containers + volumes | Manual uninstall |
| Multi-service | Docker Compose easy | Manual process management |
| Best For | VPS, production, multi-service | Development, iteration speed |

---

## 3. Real Resource Overhead of Docker on Windows

### Memory Usage

**Docker Desktop + WSL2 VM:**
- Base WSL2 VM: ~2-4GB (configurable via `.wslconfig`)
- Docker Desktop components: ~500MB-1GB
- **Total idle overhead:** ~3-5GB before any containers

**Per-Container:**
- OpenClaw gateway: ~1-2GB runtime
- Ollama (7B model): ~6-8GB
- Ollama (13B model): ~12-16GB

**Resource Saver Mode:**
- Reduces CPU and memory by 2GB+ when idle
- Automatically stops Linux VM after 5 minutes (configurable)
- **Windows WSL2 caveat:** Only pauses Docker Engine, doesn't reduce memory (use `autoMemoryReclaim` instead)

### Configuration (`.wslconfig`)

```ini
[wsl2]
processors=4
memory=8GB
swap=2GB
localhostForwarding=true

[experimental]
autoMemoryReclaim=dropcache  # Use 'dropcache' not 'gradual' (systemd conflict)
sparseVhd=true               # Prevents disk bloat
```

### CPU Overhead
- WSL2 uses all cores by default
- Windows processes can preempt WSL2
- **Recommendation:** Leave at least 2 cores for Windows

### Disk Usage
- Docker VHDX location: `%LOCALAPPDATA%\Docker\wsl\disk\docker_data.vhdx`
- Grows dynamically but doesn't shrink automatically
- **Maintenance:** `wsl --shutdown` then `Optimize-VHD` to compact

---

## 4. Would Docker Solve Current Problems?

### Security Sandbox Limits

**Current Issue:** `local-automation` agent cannot use Ollama due to sandbox isolation (OpenClaw 2026.2.24)

**Docker Assessment:**
- ✅ **Partial solution:** Docker provides stronger isolation boundaries
- ✅ **Enhanced Container Isolation (ECI):** Available in Docker Desktop
  - User namespace isolation (container root → unprivileged VM user)
  - Secured privileged containers
  - Blocks namespace sharing with host
  - **BUT:** Requires WSL 2.6+ (kernel 6.6+)
- ⚠️ **Caveat:** Mounting `docker.sock` gives container root access to host (tradeoff for sandbox mode)

**Verdict:** Docker isolation is stronger than OpenClaw's native sandbox, but introduces its own security considerations.

### Session Accumulation / Memory Leaks

**Current Issues:**
- Gateway memory leak: 389MB → 14.7GB over 4 days (#54155)
- Sessions.json unbounded growth (#55334)
- Cron jobs and subagents create sessions that persist (#43193)

**Docker Assessment:**
- ✅ **Container restart = clean slate:** Memory leaks are contained to container lifecycle
- ✅ **Health checks:** Docker can auto-restart unhealthy containers
- ✅ **Resource limits:** Can set hard memory limits per container
- ⚠️ **Not a fix:** Underlying session leak still exists, just easier to mitigate

**Verdict:** Docker makes the problem more manageable but doesn't fix the root cause.

### Backup/Restore

**Native Windows:**
- Manual backup of `~/.openclaw/` directory
- No standardized process

**Docker Assessment:**
- ✅ **Volume backups:** Standardized `docker run --rm -v vol:/source alpine tar czf backup.tar.gz -C /source .`
- ✅ **Complete stack backup:** Compose files + volumes + configs in one archive
- ✅ **Migration:** Easy to move entire stack to new host
- ✅ **Version pinning:** Can pin to specific image versions for reproducibility

**Verdict:** Docker significantly improves backup/restore story.

---

## 5. Best Practice Docker Compose Setup for AI Agent Stacks (2026)

### Recommended Architecture

```yaml
# docker-compose.yml
services:
  openclaw-gateway:
    image: ghcr.io/openclaw/openclaw:2026.2.26  # Pin version
    environment:
      HOME: /home/node
      OPENCLAW_GATEWAY_TOKEN: ${OPENCLAW_GATEWAY_TOKEN}
    volumes:
      - ${OPENCLAW_CONFIG_DIR}:/home/node/.openclaw
      - ${OPENCLAW_WORKSPACE_DIR}:/home/node/.openclaw/workspace
    ports:
      - "18789:18789"
      - "18790:18790"
    init: true
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "node", "-e", "fetch('http://127.0.0.1:18789/healthz').then((r)=>process.exit(r.ok?0:1)).catch(()=>process.exit(1))"]
      interval: 30s
      timeout: 5s
      retries: 5
      start_period: 20s
    deploy:
      resources:
        limits:
          memory: 4G  # Hard limit to contain leaks
        reservations:
          memory: 1G

  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"
    environment:
      - OLLAMA_HOST=0.0.0.0:11434
      - OLLAMA_FLASH_ATTENTION=1
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
    restart: unless-stopped

volumes:
  ollama_data:
```

### Environment Variables (`.env`)

```bash
OPENCLAW_IMAGE=ghcr.io/openclaw/openclaw:2026.2.26
OPENCLAW_GATEWAY_TOKEN=<generate-secure-token>
OPENCLAW_GATEWAY_PORT=18789
OPENCLAW_BRIDGE_PORT=18790
OPENCLAW_CONFIG_DIR=~/.openclaw
OPENCLAW_WORKSPACE_DIR=~/.openclaw/workspace
```

### Backup Script

```bash
#!/bin/bash
# backup-openclaw.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backups/openclaw/${TIMESTAMP}"
mkdir -p "$BACKUP_DIR"

# Backup config
tar czf "${BACKUP_DIR}/config.tar.gz" -C ~/.openclaw .

# Backup Ollama models (if in named volume)
docker run --rm \
  -v openclaw_ollama_data:/source:ro \
  -v "$BACKUP_DIR":/backup \
  alpine tar czf /backup/ollama_models.tar.gz -C /source .

# Backup compose files
cp docker-compose.yml .env "$BACKUP_DIR/"

echo "Backup complete: $BACKUP_DIR"
```

### Resource Management Best Practices

1. **Set memory limits:** Prevent runaway leaks with `deploy.resources.limits.memory`
2. **Use health checks:** Auto-restart on failure
3. **Enable Resource Saver:** Reduces idle resource usage
4. **Configure WSL2 limits:** Use `.wslconfig` to cap WSL2 VM size
5. **Regular pruning:** `docker system prune -a -f --volumes` to reclaim space

---

## Conclusion & Recommendation

### Is Docker Migration Worthwhile?

**Verdict:** ⚠️ **Marginal benefit for current setup, better for future scaling**

**Worth considering if:**
- You plan to deploy to VPS/cloud later (same setup works everywhere)
- You want easier backup/restore
- You run multiple services (Ollama + OpenClaw + monitoring)
- You want container restart as a "memory leak mitigation" strategy

**Not worth the hassle if:**
- Current native setup works well enough
- You prioritize iteration speed over isolation
- You don't need multi-service orchestration
- VPN issues would break your workflow

### Recommended Path Forward

1. **Short-term (native):** Continue with native Windows, use `--delete-after-run` for cron jobs, schedule gateway restarts to mitigate leaks
2. **Medium-term:** Test Docker setup on secondary machine or WSL2 without committing
3. **Long-term:** Consider Docker if deploying to VPS or adding more services

### Key Takeaway

Docker doesn't fix OpenClaw's session/memory issues - it just makes them easier to live with through container restarts and resource limits. The real value is in deployment portability and backup/restore, not in solving the current sandbox problem.

---

## Sources

1. Docker Docs - GPU Support: https://docs.docker.com/desktop/features/gpu
2. Docker Docs - WSL2 Best Practices: https://docs.docker.com/desktop/features/wsl/best-practices
3. Docker Docs - Resource Saver: https://docs.docker.com/desktop/use-desktop/resource-saver
4. Docker Docs - Enhanced Container Isolation: https://docs.docker.com/desktop/hardened-desktop/enhanced-container-isolation/
5. OneUptime - Docker Desktop Memory/CPU Limits (Feb 2026): https://oneuptime.com/blog/post/2026-02-08-how-to-configure-docker-desktop-memory-and-cpu-limits-on-windows/view
6. OneUptime - Docker Compose Backup (Feb 2026): https://oneuptime.com/blog/post/2026-02-08-how-to-back-up-docker-compose-stacks-services-volumes-config/view
7. DoneClaw - OpenClaw Docker Setup Guide (2026): https://doneclaw.com/blog/how-to-run-openclaw-in-docker-the-complete-setup-guide-2026/
8. InsiderLLM - WSL2 + Ollama Setup Guide: https://insiderllm.com/guides/wsl2-ollama-windows-setup-guide/
9. Piers Rocks - Ollama WSL2 Docker GPU: https://piers.rocks/2024/02/25/ollama-wsl2-nvidia-docker.html
10. GitHub - OpenClaw Issue #54155 (Memory Leak): https://github.com/openclaw/openclaw/issues/54155
11. GitHub - OpenClaw Issue #43193 (Session Leak): https://github.com/openclaw/openclaw/issues/43193
12. Stack Overflow - Docker Desktop 7GB Memory Usage: https://stackoverflow.com/questions/77904916/docker-desktop-using-7gb-memory-while-containers-use-no-more-than-250mb
