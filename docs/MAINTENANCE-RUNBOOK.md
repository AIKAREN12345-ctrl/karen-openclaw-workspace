# Maintenance Runbook

**Last Updated:** 2026-04-13
**Approach:** Hybrid model — OpenClaw for thinking/LLM work, Windows Task Scheduler for system automation

---

## Why This Exists

OpenClaw 2026.3.2+ blocks interpreter execution (`python`, `powershell`, `node`, `cmd /c` with complex logic). This prevents arbitrary code execution but also cripples system maintenance scripts when run through OpenClaw's `exec` tool.

**Solution:** Run maintenance tasks outside OpenClaw's sandbox using Windows Task Scheduler, while keeping OpenClaw as the orchestration and monitoring layer.

---

## System Architecture

| Layer | Responsibility | Examples |
|-------|---------------|----------|
| **OpenClaw (`agent:main`)** | Research, reasoning, coding, monitoring, alerts | Daily research, health checks, file edits |
| **Windows Task Scheduler** | System scripts, cleanup, backups, installs | Session cleanup, GitHub backup, disk checks |
| **OpenClaw `exec` (simple)** | Quick file checks, basic commands | `echo`, `dir`, simple file writes |
| **OpenClaw `web_fetch`** | Web search, API calls | SearXNG, DuckDuckGo, page fetching |

---

## Scheduled Tasks (Outside OpenClaw)

### 1. OpenClaw Session Cleanup
- **Script:** `C:\Users\Karen\.openclaw\workspace\scripts\session-cleanup.ps1`
- **Schedule:** Daily at 23:00
- **Setup:** Run `setup-cleanup-task.ps1` once in a normal PowerShell window
- **What it does:**
  - Deletes session files older than 7 days
  - Deletes checkpoint files older than 7 days
  - Deletes stale lock files older than 1 hour
  - Deletes orphaned `.deleted` files older than 1 day
  - Logs to `memory/session-cleanup.log`
- **Status:** ⏳ Pending setup (run manually once)

### 2. GitHub Backup
- **Script:** `C:\Users\Karen\.openclaw\workspace\scripts\github-backup.ps1`
- **Schedule:** Daily at 02:00 (via OpenClaw cron `BACKUP-GITHUB`)
- **What it does:** `git add -A`, commit with dated message, push to origin
- **Status:** ✅ Running

### 3. Session Archive
- **Script:** `C:\Users\Karen\.openclaw\workspace\scripts\session-archive.ps1`
- **Schedule:** Daily at 22:55 (via OpenClaw cron `ARCHIVE-SESSIONS`)
- **What it does:** Archives session history to `memory/session-archive/`
- **Status:** ✅ Running

---

## OpenClaw Cron Jobs

| Job | Time | Status |
|-----|------|--------|
| research-self-improvement | 07:00 | ✅ |
| research-openclaw | 09:00 | ✅ |
| research-kdp | 10:30 | ✅ |
| research-ai-tools | 13:00 | ✅ |
| research-local-llm | 15:00 | ✅ |
| research-security | 17:00 | ✅ |
| research-emerging-tech | 19:00 | ✅ |
| research-philosophy | 21:00 | ✅ |
| session-archive-daily | 22:55 | ✅ |
| daily-session-cleanup | 23:00 | ⚠️ Alert only (no auto-cleanup) |
| github-backup | 02:00 | ✅ |
| daily-research-reset | 00:00 | ✅ |

---

## Health Monitoring

### Manual Health Check
Run via OpenClaw tools:
1. `exec` with `echo test > .health-tmp.txt`
2. `read` the file to confirm
3. `sessions_list` to check session counts
4. `memory_search` to verify semantic search

### Automated Health Check
- **Heartbeat-based:** Updated `HEARTBEAT.md` with end-to-end verification rules
- **External script:** `scripts/health-check-e2e.ps1` (runs outside sandbox)
- **Log:** `memory/health-checks.log`

### Alert Thresholds
| Metric | Threshold | Action |
|--------|-----------|--------|
| Session count | > 100 | Warn |
| `exec` write fails | Any failure | Alert immediately |
| `memory_search` fails | Any failure | Alert immediately |
| Disk space | < 20% free | Warn |
| Disk space | < 10% free | Alert |

---

## Search Engine Stack

| Priority | Engine | Method | Status |
|----------|--------|--------|--------|
| 1 | SearXNG | `web_fetch` | ✅ Primary |
| 2 | DuckDuckGo | `web_fetch` | ✅ Fallback |
| 3 | Brave Search | Python script | ❌ Blocked by security |

---

## Known Limitations

1. **Python/PowerShell blocked in `exec`** — Use Task Scheduler for scripts
2. **PowerShell output swallowed by `exec`** — Use file writes for verification
3. **Orphan recovery loop** — Framework bug, resolved by clearing old sessions
4. **Child sessions accumulate** — Resolved by `session-cleanup.ps1`

---

## Quick Commands

### Check session count
```powershell
# Run in normal PowerShell window
(dir C:\Users\Karen\.openclaw\agents\main\sessions\*.jsonl).Count
```

### Run cleanup manually
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Karen\.openclaw\workspace\scripts\session-cleanup.ps1
```

### Create cleanup scheduled task
```powershell
powershell -ExecutionPolicy Bypass -File C:\Users\Karen\.openclaw\workspace\scripts\setup-cleanup-task.ps1
```

### Check cleanup logs
```powershell
Get-Content C:\Users\Karen\.openclaw\workspace\memory\session-cleanup.log -Tail 20
```

---

## Maintenance Checklist

**Weekly:**
- [ ] Review `memory/session-cleanup.log` for errors
- [ ] Review `memory/health-checks.log` for failures
- [ ] Check GitHub backup pushed successfully

**Monthly:**
- [ ] Verify scheduled tasks are running in Task Scheduler
- [ ] Review and prune old session archives
- [ ] Check disk space trends

**As Needed:**
- [ ] Update this runbook when adding new scripts or jobs
- [ ] Switch SearXNG instance if `search.sapti.me` goes down

---

*This runbook is a living document. Update it when the system changes.*
