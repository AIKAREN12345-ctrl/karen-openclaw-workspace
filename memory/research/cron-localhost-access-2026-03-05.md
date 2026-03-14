# Cron Jobs Accessing Local Services: Technical Solutions Research

**Date:** 2026-03-05  
**Research Focus:** Solutions for OpenClaw cron jobs to access local services (Ollama, databases) despite sandbox isolation

---

## Executive Summary

OpenClaw's `local-automation` agent type runs in an isolated sandbox that cannot access localhost services like Ollama. This is a known architectural limitation affecting many users. This document explores technical solutions ranging from configuration workarounds to architectural alternatives.

---

## 1. The Core Problem

### OpenClaw Sandbox Isolation

From GitHub issues analysis, the problem manifests in several ways:

1. **Issue #13159** - Model override ignored in isolated sessions: The `local-automation` agent cannot use Ollama because the sandbox prevents network access to localhost:11434
2. **Issue #11461** - `agents.defaults.subagents.model` config ignored in cron isolated sessions
3. **Issue #11994** - Cron jobs with `sessionTarget=isolated` + `agentTurn` never fire properly
4. **Issue #11436** - Isolated sessions reject all models except primary

### Root Cause

The OpenClaw gateway uses network namespaces or process-level isolation for `local-automation` agents. This isolation:
- Prevents access to host's localhost (127.0.0.1)
- Creates a separate network stack for the sandboxed process
- Cannot reach services bound to the host's loopback interface

**Key Quote from Issue #13159:**
> "Currently no workaround exists within OpenClaw. Users must bypass OpenClaw's session system entirely and call local models directly via system cron + API calls."

---

## 2. Network Configuration & Sandbox Bypass Techniques

### 2.1 Understanding Network Namespaces

Linux network namespaces provide complete network isolation:
- Each namespace has its own loopback interface (127.0.0.1)
- Host's localhost is NOT accessible from within the namespace
- Network interfaces, routing tables, and firewall rules are isolated

**From Unix Stack Exchange (#615868):**
> "The loopback interface in the new network namespace is not brought up automatically... The default network namespace and the new network namespace each have their own loopback interface."

### 2.2 Potential Bypass Techniques

#### A. Host Network Mode (Linux Only)

If OpenClaw supported it, running with `--network=host` would bypass isolation:

```bash
# Docker example - not applicable to OpenClaw directly
docker run --network=host myapp
```

**Limitation:** OpenClaw's sandbox doesn't expose this configuration for `local-automation` agents.

#### B. Shared Network Namespace

Creating a shared network namespace between host and sandbox:

```bash
# Create a named namespace
sudo ip netns add shared-ns

# Link host interface to namespace
sudo ip link add veth0 type veth peer name veth1
sudo ip link set veth1 netns shared-ns

# Configure routing
sudo ip addr add 10.0.0.1/24 dev veth0
sudo ip netns exec shared-ns ip addr add 10.0.0.2/24 dev veth1
```

**Feasibility:** Requires modifying OpenClaw's sandbox setup - not user-configurable.

#### C. Socket Activation (systemd)

Using systemd socket activation to pass sockets into the sandbox:

```ini
# /etc/systemd/system/myapp.socket
[Socket]
ListenStream=127.0.0.1:11434
[Install]
WantedBy=sockets.target
```

**Feasibility:** Requires OpenClaw to support socket passing - not currently available.

---

## 3. Reverse Proxy Solutions

### 3.1 Local Reverse Proxy Architecture

A reverse proxy can bridge the gap between sandbox and host services:

```
┌─────────────────────────────────────────────────────────────┐
│                        Host System                          │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────┐  │
│  │   OpenClaw   │      │   Reverse    │      │  Ollama  │  │
│  │   Sandbox    │──────▶│   Proxy      │──────▶│:11434    │  │
│  │              │      │  :8080       │      │          │  │
│  └──────────────┘      └──────────────┘      └──────────┘  │
│                              │                              │
│                              │ (binds to 0.0.0.0)           │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 Implementation Options

#### Option A: Nginx Reverse Proxy

```nginx
# /etc/nginx/conf.d/ollama-proxy.conf
server {
    listen 0.0.0.0:8080;
    location / {
        proxy_pass http://127.0.0.1:11434;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Security Considerations:**
- Binding to 0.0.0.0 exposes service to all network interfaces
- Firewall rules should restrict access: `iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT`

#### Option B: Caddy (Simpler Config)

```caddyfile
# Caddyfile
:8080 {
    reverse_proxy localhost:11434
    bind 0.0.0.0
}
```

#### Option C: Simple Python Proxy

```python
# quick_proxy.py - minimal reverse proxy
import http.server
import socketserver
import urllib.request

PORT = 8080
TARGET = "http://127.0.0.1:11434"

class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        url = TARGET + self.path
        with urllib.request.urlopen(url) as response:
            self.send_response(response.status)
            for header, value in response.headers.items():
                self.send_header(header, value)
            self.end_headers()
            self.wfile.write(response.read())
    
    do_POST = do_GET

with socketserver.TCPServer(("0.0.0.0", PORT), ProxyHandler) as httpd:
    print(f"Proxy listening on port {PORT}")
    httpd.serve_forever()
```

### 3.3 Windows-Specific Considerations

On Windows (the user's environment), network isolation works differently:

- Windows containers use different isolation modes: `process` vs `hyperv`
- WSL2 has its own network translation layer
- `localhost` in WSL2 refers to the WSL2 VM, not Windows host

**Workaround for Windows:**
```powershell
# In WSL2, use host.docker.internal or Windows host IP
# From Windows, bind proxy to 0.0.0.0 but firewall restrict
netsh advfirewall firewall add rule name="Ollama Proxy" dir=in action=allow protocol=tcp localport=8080 remoteip=127.0.0.1
```

---

## 4. Docker/Container Approaches

### 4.1 Running Ollama in Docker with Shared Network

```yaml
# docker-compose.yml
version: '3'
services:
  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    networks:
      - shared-network
    volumes:
      - ollama-data:/root/.ollama

  openclaw-bridge:
    image: alpine/socat
    command: tcp-listen:11434,fork,reuseaddr tcp-connect:ollama:11434
    networks:
      - shared-network
    ports:
      - "0.0.0.0:11435:11434"  # Exposed to host

networks:
  shared-network:
    driver: bridge

volumes:
  ollama-data:
```

### 4.2 Sidecar Pattern

Run a sidecar container that bridges sandbox to host:

```yaml
# Sidecar pattern for OpenClaw
version: '3'
services:
  bridge:
    image: alpine/socat
    command: >
      tcp-listen:11434,fork,reuseaddr,bind=0.0.0.0
      tcp-connect:host.docker.internal:11434
    ports:
      - "11434:11434"
```

---

## 5. Systemd Service Integration

### 5.1 Creating a Systemd Service for Ollama Bridge

```ini
# /etc/systemd/system/ollama-bridge.service
[Unit]
Description=Ollama Bridge for OpenClaw
After=network.target ollama.service

[Service]
Type=simple
ExecStart=/usr/bin/socat tcp-listen:11435,fork,reuseaddr,bind=0.0.0.0 tcp-connect:127.0.0.1:11434
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5.2 Windows Service Alternative

```powershell
# Create Windows service using nssm (Non-Sucking Service Manager)
nssm install OllamaBridge "C:\tools\socat.exe" "tcp-listen:11435,fork,reuseaddr,bind=0.0.0.0 tcp-connect:127.0.0.1:11434"
nssm start OllamaBridge
```

---

## 6. Alternative Architectures

### 6.1 Message Queue Approach

Instead of direct API calls, use a message queue:

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   OpenClaw   │     │   Message    │     │   Ollama     │
│   Sandbox    │────▶│   Queue      │◀────│   Worker     │
│              │     │  (Redis/     │     │  (on host)   │
│              │     │   RabbitMQ)  │     │              │
└──────────────┘     └──────────────┘     └──────────────┘
```

**Implementation:**

```python
# ollama_worker.py - runs on host
import redis
import requests
import json

r = redis.Redis(host='localhost', port=6379, db=0)

while True:
    # Wait for job from queue
    _, job = r.brpop('ollama-jobs')
    job_data = json.loads(job)
    
    # Call local Ollama
    response = requests.post(
        'http://localhost:11434/api/generate',
        json=job_data['prompt']
    )
    
    # Store result
    r.set(f"result:{job_data['id']}", response.text)
```

### 6.2 Local API Gateway Pattern

Create a local API gateway that both OpenClaw and other services can use:

```python
# local_api_gateway.py
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    # Forward to Ollama
    response = requests.post(
        'http://localhost:11434/v1/chat/completions',
        json=request.json
    )
    return jsonify(response.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```

### 6.3 File-Based Communication

For simple use cases, use file-based IPC:

```python
# request_handler.py
import os
import json
import time
from pathlib import Path

REQUEST_DIR = Path('/tmp/ollama-requests')
RESPONSE_DIR = Path('/tmp/ollama-responses')

def submit_request(prompt):
    req_id = str(time.time())
    request_file = REQUEST_DIR / f"{req_id}.json"
    response_file = RESPONSE_DIR / f"{req_id}.json"
    
    # Write request
    request_file.write_text(json.dumps({'prompt': prompt, 'id': req_id}))
    
    # Wait for response (with timeout)
    for _ in range(60):  # 60 seconds
        if response_file.exists():
            result = json.loads(response_file.read_text())
            response_file.unlink()
            request_file.unlink()
            return result
        time.sleep(1)
    
    raise TimeoutError("No response received")
```

---

## 7. Security Implications

### 7.1 Risk Assessment by Approach

| Approach | Risk Level | Mitigation |
|----------|-----------|------------|
| Reverse proxy (0.0.0.0) | **HIGH** | Firewall rules, authentication |
| Shared network namespace | **MEDIUM** | Limited to specific services |
| Message queue | **LOW** | Authentication, TLS |
| File-based IPC | **LOW** | File permissions, sandbox escape risk |
| Systemd socket activation | **MEDIUM** | Proper socket permissions |

### 7.2 Recommended Security Practices

1. **Firewall Rules:**
   ```bash
   # Linux - only allow localhost
   iptables -A INPUT -p tcp --dport 8080 -s 127.0.0.1 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8080 -j DROP
   ```

2. **Authentication:**
   - Use API keys even for local services
   - Implement request signing

3. **TLS:**
   - Use self-signed certificates for localhost
   - Certificate pinning for added security

4. **Monitoring:**
   - Log all proxy access
   - Alert on unusual patterns

---

## 8. Recommended Solutions for OpenClaw + Ollama

### Immediate Workaround (No Code Changes)

**Use `agent:main` instead of `local-automation`:**

```json
{
  "name": "Ollama Health Check",
  "schedule": {"kind": "every", "everyMs": 3600000},
  "payload": {
    "kind": "agentTurn",
    "message": "Check Ollama status",
    "model": "ollama/qwen2.5:14b"
  },
  "sessionTarget": "main",
  "enabled": true
}
```

**Trade-offs:**
- ✅ Works immediately
- ✅ No additional infrastructure
- ❌ Uses main session (not isolated)
- ❌ May interfere with interactive use

### Short-Term Solution (Minimal Setup)

**Reverse Proxy with Localhost Binding:**

1. Install socat or nginx
2. Configure proxy to bind to 0.0.0.0:11435 → 127.0.0.1:11434
3. Configure OpenClaw to use `http://host.docker.internal:11435` (Windows) or `http://<host-ip>:11435` (Linux)
4. Firewall restrict to localhost only

### Long-Term Solution (Robust)

**Message Queue Architecture:**

1. Deploy Redis or RabbitMQ accessible from both host and sandbox
2. Create Ollama worker service on host
3. Modify OpenClaw jobs to submit requests to queue
4. Worker processes and returns results

**Benefits:**
- Decouples OpenClaw from direct service access
- Scalable to multiple workers
- Resilient to temporary failures

---

## 9. OpenClaw-Specific Configuration

### 9.1 Current Workarounds from Community

From GitHub issue analysis, users have found:

1. **Per-agent model config (Issue #13159, comment by Starefossen):**
   ```json
   {
     "agents": {
       "list": [
         {"id": "main"},
         {
           "id": "planner",
           "model": {
             "primary": "ollama/qwen2.5:14b"
           }
         }
       ]
     }
   }
   ```

2. **Explicit model in cron payload:**
   ```json
   {
     "payload": {
       "model": "ollama/qwen2.5:14b",
       "message": "..."
     }
   }
   ```

### 9.2 Version Compatibility

- **2026.2.24:** Did NOT fix the sandbox isolation issue
- **2026.3.x:** May have partial fixes for model routing but sandbox isolation remains
- **Workaround status:** Still required as of March 2026

---

## 10. Implementation Checklist

### For Windows Users (Current Environment)

- [ ] Verify Ollama is running on `127.0.0.1:11434`
- [ ] Install socat or nginx for Windows
- [ ] Configure proxy: `0.0.0.0:11435` → `127.0.0.1:11434`
- [ ] Add Windows Firewall rule restricting 11435 to localhost
- [ ] Test proxy access from PowerShell: `curl http://localhost:11435`
- [ ] Update OpenClaw config to use `http://localhost:11435`
- [ ] Test cron job with `sessionTarget: main` first
- [ ] Monitor for any sandbox-related failures

### For Linux Users

- [ ] Configure Ollama to bind to both localhost and network interface
- [ ] Set up nginx reverse proxy with localhost-only access
- [ ] Use iptables to restrict access
- [ ] Consider systemd socket activation for better security

---

## 11. References

### OpenClaw GitHub Issues
- [#13159](https://github.com/openclaw/openclaw/issues/13159) - Model override ignored in isolated sessions
- [#11461](https://github.com/openclaw/openclaw/issues/11461) - agents.defaults.subagents.model ignored
- [#11994](https://github.com/openclaw/openclaw/issues/11994) - Cron jobs with sessionTarget=isolated never fire
- [#11436](https://github.com/openclaw/openclaw/issues/11436) - Isolated sessions reject all models except primary

### Technical Resources
- [Unix Stack Exchange - Access localhost from network namespace](https://unix.stackexchange.com/questions/615868/access-localhost-from-network-namespace)
- [Sigma Star - Restricting network access using Linux namespaces](https://sigma-star.at/blog/2023/05/sandbox-netns/)
- [Red Hat - Building Linux containers using namespaces](https://www.redhat.com/en/blog/building-container-namespaces)

### Tools Mentioned
- **socat** - Multipurpose relay for bidirectional data transfer
- **nginx** - Web server and reverse proxy
- **Caddy** - Modern reverse proxy with automatic HTTPS
- **Traefik** - Cloud-native reverse proxy
- **Redis/RabbitMQ** - Message queues for decoupled architecture

---

## 12. Conclusion

The OpenClaw sandbox isolation preventing localhost access is a fundamental security feature, not a bug. However, it creates friction for legitimate use cases like accessing local Ollama instances.

**Recommended Path Forward:**

1. **Immediate:** Use `sessionTarget: main` for Ollama-dependent cron jobs
2. **Short-term:** Implement a reverse proxy with proper firewall restrictions
3. **Long-term:** Consider migrating to a message queue architecture for better decoupling

The community has been vocal about this limitation, and several GitHub issues track related problems. Until OpenClaw provides native support for configurable sandbox network policies, the reverse proxy approach offers the best balance of functionality and security.

---

*Document generated by subagent research session - 2026-03-05*
