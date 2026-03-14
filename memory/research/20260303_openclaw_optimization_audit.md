# OpenClaw System Optimization & Improvements Audit

**Date:** 2026-03-03  
**OpenClaw Version:** 2026.2.25 (Update available: 2026.3.2)  
**Node:** DESKTOP-M8AO8LN (Windows 11)  
**System:** 24GB RAM, Ollama installed  

---

## Executive Summary

This audit identifies **12 prioritized improvements** across 6 categories: Security (4 items), Performance (3 items), Missing Features (2 items), Backup/Recovery (1 item), Integrations (1 item), and Health Monitoring (1 item).

**Critical Issues Found:**
- 2 CRITICAL security findings from audit
- Memory search non-functional (missing embedding provider)
- Subagent/Ollama sandbox isolation still unresolved
- Outdated OpenClaw version (2026.2.25 vs 2026.3.2)

---

## 1. Security Hardening

### Current Security Posture

From `openclaw security audit`:
- **2 CRITICAL** findings
- **2 WARN** findings
- **1 INFO** finding

### Finding 1: CRITICAL - Host-Header Origin Fallback (HIGH PRIORITY)

**Issue:** `gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback=true` weakens DNS rebinding protections.

**Current Config:**
```json
"gateway": {
  "controlUi": {
    "dangerouslyAllowHostHeaderOriginFallback": true
  }
}
```

**Risk:** Allows websocket origin checks to fall back to Host header, potentially enabling DNS rebinding attacks.

**Remediation:**
```json
"gateway": {
  "controlUi": {
    "dangerouslyAllowHostHeaderOriginFallback": false,
    "allowedOrigins": ["http://localhost:18788", "http://100.75.72.26:18788"]
  }
}
```

**Risk/Benefit:**
- **Risk:** Low - requires explicit origin configuration
- **Benefit:** High - closes DNS rebinding attack vector
- **Effort:** 5 minutes

---

### Finding 2: CRITICAL - Small Model Security (MEDIUM PRIORITY)

**Issue:** `local-automation` agent uses qwen2.5:14b with sandbox=off and web tools enabled.

**Current Config:**
```json
{
  "id": "local-automation",
  "model": "ollama/qwen2.5:14b",
  // sandbox not explicitly enabled
}
```

**Risk:** Small models (<300B params) with web tool access can be manipulated by untrusted inputs.

**Remediation Options:**

**Option A - Enable Sandbox (Recommended for shared use):**
```json
"agents": {
  "defaults": {
    "sandbox": {
      "mode": "all"
    }
  }
}
```

**Option B - Disable Web Tools for Local Agent:**
```json
"agents": {
  "list": [
    {
      "id": "local-automation",
      "tools": {
        "deny": ["web_search", "web_fetch", "browser"]
      }
    }
  ]
}
```

**Option C - Accept Risk (Current - OK for single-user home use):**
- Document that this is a personal assistant deployment
- No untrusted users have access

**Risk/Benefit:**
- **Risk:** Medium - only if untrusted users gain access
- **Benefit:** Medium - defense in depth
- **Effort:** 10 minutes

---

### Finding 3: WARN - Multi-User Setup Heuristic (LOW PRIORITY)

**Issue:** Telegram group allowlist configured triggers multi-user warning.

**Current Config:**
```json
"channels": {
  "telegram": {
    "groupPolicy": "allowlist",
    "groupAllowFrom": [8378714141]
  }
}
```

**Assessment:** This is a false positive for home use. The group allowlist is for the user's own Telegram groups.

**Action:** No change needed. Document as "intentional - personal use only."

---

### Finding 4: WARN - Insecure Flags Enabled (INFO)

**Issue:** Same as Finding 1 (dangerouslyAllowHostHeaderOriginFallback).

**Action:** Addressed in Finding 1 remediation.

---

### Additional Security Recommendations

#### A. Gateway Token Rotation
- **Current:** 64-character token (good)
- **Action:** Schedule rotation every 90 days
- **Command:** `openclaw gateway rotate-token`

#### B. Rate Limiting Review
- **Current:** 10 attempts/min, 5min lockout
- **Status:** Adequate for home use

#### C. Telegram Bot Token Security
- **Current:** Stored in config
- **Risk:** Low - home machine, single user
- **Future:** Consider environment variable: `${TELEGRAM_BOT_TOKEN}`

---

## 2. Performance Optimization

### Issue 1: Memory Search Non-Functional (HIGH PRIORITY)

**Problem:** Memory search provider set to "local" but model path points to non-existent directory.

**Current Config:**
```json
"memorySearch": {
  "enabled": true,
  "provider": "local",
  "local": {
    "modelPath": "C:\\Users\\Karen\\.node-llama-cpp\\models\\hf_nomic-ai_nomic-embed-text-v1.5.Q8_0.gguf"
  }
}
```

**Issue:** File may not exist at this path.

**Remediation - Switch to Ollama Embeddings:**
```json
"memorySearch": {
  "enabled": true,
  "provider": "ollama",
  "ollama": {
    "baseUrl": "http://localhost:11434",
    "model": "nomic-embed-text"
  },
  "query": {
    "hybrid": {
      "enabled": true,
      "vectorWeight": 0.7,
      "textWeight": 0.3
    }
  },
  "cache": {
    "enabled": true,
    "maxEntries": 50000
  }
}
```

**Prerequisites:**
```bash
ollama pull nomic-embed-text
```

**Risk/Benefit:**
- **Risk:** Low - Ollama already running
- **Benefit:** High - enables semantic memory search
- **Effort:** 10 minutes

---

### Issue 2: Cron Job Efficiency (MEDIUM PRIORITY)

**Current Jobs Analysis:**

| Job | Schedule | Target | Issue |
|-----|----------|--------|-------|
| pulse-check | */30 min | main | Uses Python - OK |
| ollama-monitor | */2 hours | isolated | May use local-automation |
| ollama-research | */4 hours | isolated | May use local-automation |
| memory-log | :25 hourly | isolated | Uses local-automation |
| github-backup | 2 AM daily | main | Git commands - OK |

**Problem:** Jobs targeting `local-automation` agent with Ollama fail due to sandbox isolation.

**Remediation:**

**Option A - Switch to agent:main (Recommended):**
```bash
openclaw cron edit <job-id> --clear-agent
# Or edit jobs.json:
"agentId": "main"
```

**Option B - Use systemEvent instead of agentTurn:**
```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "python script.py"
  }
}
```

**Option C - Use isolated session with no agent:**
```json
{
  "sessionTarget": "isolated",
  "agentId": null
}
```

**Risk/Benefit:**
- **Risk:** Low - job behavior unchanged
- **Benefit:** Medium - fixes failing jobs
- **Effort:** 15 minutes

---

### Issue 3: Model Selection Optimization (MEDIUM PRIORITY)

**Current Models:**

| Model | Size | Use Case | Status |
|-------|------|----------|--------|
| k2p5 | Cloud | Interactive | ✓ Good |
| qwen2.5:14b | 14B | Local automation | ✓ Good |

**Recommendations:**

1. **Add qwen2.5:7b for lighter tasks:**
   - Smaller than 14b (4.7GB vs ~9GB)
   - Faster inference
   - Good for cron jobs
   ```bash
   ollama pull qwen2.5:7b
   ```

2. **Configure model routing:**
   ```json
   "agents": {
     "list": [
       {
         "id": "local-automation",
         "model": "ollama/qwen2.5:7b"
       }
     ]
   }
   ```

3. **Remove unused models:**
   - llama3.2:3b (tool calling issues)
   - gemma:2b (no tool support)

**Risk/Benefit:**
- **Risk:** Low - just downloading models
- **Benefit:** Medium - faster local inference
- **Effort:** 10 minutes

---

### Issue 4: Disk Space Management (LOW PRIORITY)

**Current State:**
- Memory files: 12 daily files + research folder
- Ollama models: Multiple installed
- Git repository: Daily commits

**Recommendations:**

1. **Log rotation for memory files:**
   - Archive files older than 30 days
   - Compress to .zip or .gz

2. **Ollama model cleanup:**
   ```bash
   ollama list
   ollama rm llama3.2:3b  # if still present
   ollama rm gemma:2b     # if still present
   ```

3. **Git repository maintenance:**
   - Current: Daily commits
   - Consider: Weekly squash for old history

**Risk/Benefit:**
- **Risk:** Low - just cleanup
- **Benefit:** Low - prevent future issues
- **Effort:** 20 minutes

---

## 3. Missing Features/Utilities

### Gap 1: Health Check Skill Underutilized (HIGH PRIORITY)

**Current State:** Healthcheck skill installed but no scheduled security audits.

**Recommendation:** Schedule periodic security audits.

**Implementation:**
```bash
# Daily security audit
openclaw cron add \
  --name "security-audit" \
  --cron "0 3 * * *" \
  --session isolated \
  --message "Run 'openclaw security audit' and report any new critical findings" \
  --no-deliver

# Weekly deep audit
openclaw cron add \
  --name "security-audit-deep" \
  --cron "0 4 * * 0" \
  --session isolated \
  --message "Run 'openclaw security audit --deep' and summarize findings" \
  --announce
```

**Risk/Benefit:**
- **Risk:** Low - read-only audit
- **Benefit:** High - proactive security monitoring
- **Effort:** 5 minutes

---

### Gap 2: Missing Skills Catalog (MEDIUM PRIORITY)

**Potentially Useful Skills:**

| Skill | Use Case | Priority |
|-------|----------|----------|
| calendar | Google/Outlook calendar integration | High |
| email | IMAP/SMTP email management | High |
| rss | News feed monitoring | Medium |
| home-assistant | Smart home control | Medium |
| docker | Container management | Low |
| ssh | Remote server management | Low |

**Current Skills:**
- healthcheck ✓
- skill-creator ✓
- weather ✓
- himalaya (email) ✓
- local-llm ✓

**Recommendation:** Install calendar skill for schedule awareness.

---

### Gap 3: Automation Opportunities (MEDIUM PRIORITY)

**Current Automation:**
- Hourly memory logging
- Daily Git backup
- Periodic Ollama monitoring

**Suggested Additions:**

1. **Disk space alert:**
   ```bash
   openclaw cron add \
     --name "disk-check" \
     --cron "0 */6 * * *" \
     --session isolated \
     --message "Check disk space. Alert if < 10GB free." \
     --no-deliver
   ```

2. **Memory file cleanup:**
   - Archive files older than 30 days
   - Run weekly

3. **OpenClaw update check:**
   ```bash
   openclaw cron add \
     --name "update-check" \
     --cron "0 9 * * 1" \
     --session main \
     --system-event "Check for OpenClaw updates: openclaw update status"
   ```

---

## 4. Backup and Recovery

### Current State (GOOD)

**Git Backup:**
- Repository: AIKAREN12345-ctrl/karen-openclaw-workspace
- Schedule: Daily at 2 AM
- Scope: Entire workspace

**Config Backup:**
- `openclaw.json` - Main config
- `node.json` - Node config
- `jobs.json` - Cron jobs
- All in workspace, git-tracked

### Improvement: Config Versioning (MEDIUM PRIORITY)

**Issue:** Config changes not explicitly versioned.

**Recommendation:** Add config snapshot before major changes.

**Implementation:**
```bash
# Pre-change backup script
openclaw config export > workspace/config-backups/openclaw-$(date +%Y%m%d).json
```

**Or as cron job:**
```bash
openclaw cron add \
  --name "config-backup" \
  --cron "0 1 * * *" \
  --session main \
  --system-event "Backup OpenClaw configs to git"
```

---

### Disaster Recovery Plan

**Scenario 1: Config Corruption**
1. Restore from git: `git checkout <commit> -- openclaw.json`
2. Restart gateway: `openclaw gateway restart`

**Scenario 2: Complete Reinstall**
1. Install OpenClaw: `npm install -g openclaw`
2. Clone workspace: `git clone <repo>`
3. Copy configs: `cp workspace/configs/* ~/.openclaw/`
4. Restart: `openclaw gateway restart`

**Scenario 3: Node Loss**
1. Pair new node: `openclaw node pair`
2. Install Ollama on new machine
3. Pull models: `ollama pull qwen2.5:14b`
4. Update node references in configs

---

## 5. Integration Opportunities

### Integration 1: Calendar Connectivity (HIGH PRIORITY)

**Current Gap:** No calendar integration for schedule awareness.

**Options:**

1. **Google Calendar via gcalcli:**
   - Install: `pip install gcalcli`
   - Auth: OAuth flow
   - Usage: `gcalcli agenda`

2. **Outlook/Exchange:**
   - Use `himalaya` skill (already installed)
   - Calendar via IMAP/CalDAV

3. **Local .ics files:**
   - Parse calendar exports
   - No cloud dependency

**Implementation:**
```bash
# Add to skills or cron
openclaw cron add \
  --name "morning-briefing" \
  --cron "0 7 * * *" \
  --session isolated \
  --message "Check calendar for today and generate briefing" \
  --announce
```

---

### Integration 2: Home Assistant (MEDIUM PRIORITY)

**Use Case:** Smart home control via OpenClaw.

**Requirements:**
- Home Assistant instance running
- Long-lived access token
- API endpoint configured

**Implementation:**
```json
"skills": {
  "home-assistant": {
    "enabled": true,
    "config": {
      "url": "http://homeassistant.local:8123",
      "token": "${HA_TOKEN}"
    }
  }
}
```

---

### Integration 3: API Integrations (LOW PRIORITY)

**Potential APIs:**
- Todoist/Things (task management)
- Spotify (music control)
- Weather API (more detailed than wttr.in)
- News API (headlines)

---

## 6. Health Monitoring

### Current Monitoring (PARTIAL)

**Existing:**
- `pulse-check` every 30 min
- `ollama-monitor` every 2 hours
- `openclaw security audit` - manual only

### Improvement 1: System Health Dashboard (MEDIUM PRIORITY)

**Create comprehensive health check:**

```bash
openclaw cron add \
  --name "system-health" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Check: disk space, memory usage, Ollama status, OpenClaw version, last backup time. Report anomalies." \
  --no-deliver
```

**Metrics to Track:**
- Disk space (< 10GB alert)
- Memory usage
- Ollama availability
- OpenClaw version (update available?)
- Last successful backup
- Failed cron jobs (consecutive errors)

---

### Improvement 2: Alerting Mechanisms (MEDIUM PRIORITY)

**Current:** Telegram bot (working)

**Enhancement:** Failure alerts for cron jobs.

**Implementation:**
```bash
openclaw cron edit <job-id> \
  --failure-alert \
  --failure-alert-after 3 \
  --failure-alert-channel telegram \
  --failure-alert-to "8378714141"
```

---

### Improvement 3: Proactive Maintenance (LOW PRIORITY)

**Scheduled Tasks:**

1. **Weekly:**
   - Log rotation
   - Model cleanup
   - Dependency updates

2. **Monthly:**
   - Security audit review
   - Token rotation
   - Backup verification

3. **Quarterly:**
   - Full system review
   - Skill updates
   - Documentation refresh

---

## Prioritized Action Plan

### Immediate (Do Today)

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 1 | Fix memory search (switch to Ollama embeddings) | 10 min | High |
| 2 | Disable host-header fallback | 5 min | High |
| 3 | Update OpenClaw to 2026.3.2 | 10 min | Medium |
| 4 | Fix local-automation cron jobs (switch to main) | 15 min | Medium |

### This Week

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 5 | Schedule security audit cron job | 5 min | High |
| 6 | Pull qwen2.5:7b for lighter tasks | 10 min | Medium |
| 7 | Clean up unused Ollama models | 5 min | Low |
| 8 | Add disk space monitoring | 10 min | Medium |

### This Month

| Priority | Item | Effort | Impact |
|----------|------|--------|--------|
| 9 | Install calendar skill | 30 min | High |
| 10 | Review and document disaster recovery | 30 min | Medium |
| 11 | Enable cron job failure alerts | 15 min | Medium |
| 12 | Consider sandbox mode for local-automation | 20 min | Low |

---

## Risk/Benefit Summary

### High Impact, Low Risk (Do First)
1. Fix memory search
2. Disable host-header fallback
3. Schedule security audits

### High Impact, Medium Risk (Plan Carefully)
4. Update OpenClaw (test first)
5. Fix cron job agents

### Medium Impact, Low Risk (Do When Convenient)
6. Add disk monitoring
7. Model cleanup
8. Failure alerts

### Medium Impact, Medium Effort (Schedule)
9. Calendar integration
10. Disaster recovery docs

---

## Appendix: Quick Commands

```bash
# Check current status
openclaw status --deep

# Security audit
openclaw security audit

# Update OpenClaw
openclaw update

# List cron jobs
openclaw cron list

# Edit a cron job
openclaw cron edit <id> --no-deliver

# Pull Ollama model
ollama pull qwen2.5:7b
ollama pull nomic-embed-text

# List Ollama models
ollama list

# Remove Ollama model
ollama rm <model>
```

---

## References

- OpenClaw Docs: https://docs.openclaw.ai
- Security Audit: `openclaw security audit --deep`
- Current Config: `~/.openclaw/openclaw.json`
- Cron Jobs: `~/.openclaw/cron/jobs.json`
- Memory System Research: `memory/research/20260303_memory_system_research.md`
- Cron Control Research: `memory/research/20260303_cron_job_control_2026.3.1.md`
- Migration Guide: `memory/research/20260303_openclaw_2026.3.1_migration.md`

---

*Research completed: 2026-03-03*  
*Next review recommended: 2026-04-03*
