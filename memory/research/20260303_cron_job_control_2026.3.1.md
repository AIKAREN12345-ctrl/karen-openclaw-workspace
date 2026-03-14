# OpenClaw Cron Job Configuration Research - Version 2026.3.1

**Research Date:** 2026-03-03  
**OpenClaw Version:** 2026.3.1 (2a8ac97)  
**Target File:** C:\Users\Karen\.openclaw\workspace\memory\research\20260303_cron_job_control_2026.3.1.md

---

## Executive Summary

OpenClaw 2026.3.1 introduces significant changes to cron job notification control. The `wakeMode` setting is **NOT deprecated** but works differently with the new `delivery` system. The key finding is that `--no-deliver` (or `delivery.mode: "none"`) is the primary mechanism to silence cron job notifications.

---

## 1. How to Control Cron Job Notifications in 2026.3.1

### Key Finding: The `delivery` Configuration Object

In 2026.3.1, cron job notifications are controlled through the `delivery` configuration object, not just `wakeMode`.

### Delivery Modes

| Mode | Behavior | Use Case |
|------|----------|----------|
| `announce` | Deliver summary to chat + brief summary to main session | Default for isolated jobs |
| `webhook` | POST finished event payload to URL | External integrations |
| `none` | Internal only - no delivery, no main-session summary | Silent background jobs |

### CLI Options for Notification Control

```bash
# Silent job - no notifications at all
openclaw cron add \
  --name "silent-job" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Run background task" \
  --no-deliver

# Announce to specific channel
openclaw cron add \
  --name "channel-job" \
  --cron "0 9 * * *" \
  --session isolated \
  --message "Morning briefing" \
  --announce \
  --channel telegram \
  --to "-1001234567890"

# Webhook delivery
openclaw cron add \
  --name "webhook-job" \
  --cron "0 */2 * * *" \
  --session isolated \
  --message "System check" \
  --channel webhook \
  --to "https://example.com/webhook"
```

### JSON Configuration for Silent Jobs

```json
{
  "name": "Silent Background Task",
  "schedule": { "kind": "cron", "expr": "0 */6 * * *" },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "Run background maintenance"
  },
  "delivery": {
    "mode": "none"
  }
}
```

---

## 2. What Happened to wakeMode? Is It Deprecated?

### Answer: NO - wakeMode is NOT Deprecated

The `wakeMode` setting is **still active and functional** in 2026.3.1. However, its role has been refined:

### wakeMode Behavior

| Value | Behavior |
|-------|----------|
| `now` (default) | Triggers immediate heartbeat/run |
| `next-heartbeat` | Waits for next scheduled heartbeat |

### How wakeMode Interacts with Delivery

**For Main Session Jobs:**
- `wakeMode: "now"` → Immediate system event processing
- `wakeMode: "next-heartbeat"` → Event waits for next heartbeat

**For Isolated Jobs:**
- `wakeMode` controls when the **main-session summary** posts (only when `delivery.mode = "announce"`)
- `wakeMode: "now"` → Immediate main-session summary
- `wakeMode: "next-heartbeat"` → Waits for next heartbeat to post summary

**Important:** When `delivery.mode: "none"`, `wakeMode` has no visible effect since no summary is posted.

### Current CLI Help for wakeMode

```
--wake <mode>          Wake mode (now|next-heartbeat) (default: "now")
```

---

## 3. Alternative Ways to Silence Cron Jobs

### Method 1: --no-deliver (Recommended)

```bash
openclaw cron add \
  --name "silent-task" \
  --cron "0 */4 * * *" \
  --session isolated \
  --message "Background processing" \
  --no-deliver
```

### Method 2: delivery.mode = "none" (JSON)

```json
{
  "name": "Silent Task",
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "none"
  }
}
```

### Method 3: Main Session with System Event (No Announce)

```bash
openclaw cron add \
  --name "quiet-check" \
  --every "2h" \
  --session main \
  --system-event "Check system status" \
  --wake next-heartbeat
```

Main session jobs don't announce by default - they only add to the heartbeat context.

### Method 4: Disable the Job (Temporary)

```bash
openclaw cron disable <job-id>
```

### Method 5: Use --best-effort-deliver (Fail-Silent)

```bash
openclaw cron add \
  --name "best-effort" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Background task" \
  --announce \
  --best-effort-deliver
```

This prevents job failure if delivery fails, but still attempts delivery.

---

## 4. Best Practices for Cron Job Scheduling

### A. Choose the Right Session Target

| Use Case | Session Target | Payload Type |
|----------|---------------|--------------|
| Background tasks, no output needed | `isolated` | `agentTurn` + `delivery.mode: "none"` |
| Daily reports with summary | `isolated` | `agentTurn` + `delivery.mode: "announce"` |
| Context-aware reminders | `main` | `systemEvent` |
| One-shot reminders | `main` | `systemEvent` |

### B. Use Appropriate Staggering

```bash
# Default stagger (up to 5 min for top-of-hour jobs)
openclaw cron add --name "hourly" --cron "0 * * * *" --session isolated --message "Hourly check"

# Explicit stagger
openclaw cron add --name "staggered" --cron "0 * * * *" --stagger 30s --session isolated --message "Staggered check"

# No stagger (exact timing)
openclaw cron add --name "exact" --cron "0 9 * * *" --exact --session isolated --message "Exact 9am"
```

### C. Set Reasonable Timeouts

```bash
# Short task
openclaw cron add --name "quick" --every "10m" --timeout-seconds 60 --session isolated --message "Quick check"

# Long analysis
openclaw cron add --name "deep" --cron "0 2 * * 0" --timeout-seconds 600 --session isolated --message "Weekly analysis"
```

### D. Use Timezones for Location-Specific Jobs

```bash
openclaw cron add \
  --name "morning-brief" \
  --cron "0 7 * * *" \
  --tz "America/New_York" \
  --session isolated \
  --message "Generate morning briefing"
```

### E. Clean Up One-Shot Jobs

```bash
# Auto-delete after success (default for --at jobs)
openclaw cron add \
  --name "reminder" \
  --at "30m" \
  --session main \
  --system-event "Check email" \
  --wake now \
  --delete-after-run
```

### F. Use Model Overrides for Heavy Tasks

```bash
openclaw cron add \
  --name "weekly-analysis" \
  --cron "0 6 * * 1" \
  --session isolated \
  --message "Deep codebase analysis" \
  --model "ollama/qwen2.5:14b" \
  --thinking low \
  --no-deliver
```

### G. Organize with Descriptions

```bash
openclaw cron add \
  --name "backup" \
  --description "Daily git backup to remote" \
  --cron "0 2 * * *" \
  --session main \
  --system-event "Run git backup" \
  --wake next-heartbeat
```

---

## 5. New Cron Features in 2026.3.1

### Feature 1: Enhanced Delivery System

The `delivery` object replaces legacy `notify` and provides granular control:

```json
{
  "delivery": {
    "mode": "announce",      // none | announce | webhook
    "channel": "telegram",   // last | whatsapp | telegram | discord | ...
    "to": "-1001234567890",  // channel-specific target
    "bestEffort": true       // don't fail on delivery error
  }
}
```

### Feature 2: Failure Alert Configuration

```bash
# Enable failure alerts
openclaw cron edit <job-id> \
  --failure-alert \
  --failure-alert-after 3 \
  --failure-alert-channel telegram \
  --failure-alert-to "-1001234567890" \
  --failure-alert-cooldown "1h"

# Disable failure alerts
openclaw cron edit <job-id> --no-failure-alert
```

### Feature 3: Lightweight Context Option

```bash
# Use lightweight bootstrap for faster isolated jobs
openclaw cron add \
  --name "quick-check" \
  --every "5m" \
  --session isolated \
  --light-context \
  --message "Quick status check"
```

### Feature 4: Thinking Level Control

```bash
openclaw cron add \
  --name "analysis" \
  --cron "0 */6 * * *" \
  --session isolated \
  --message "Analyze trends" \
  --thinking medium
```

### Feature 5: Agent Binding

```bash
# Pin job to specific agent
openclaw cron add \
  --name "ops-check" \
  --cron "0 */2 * * *" \
  --session isolated \
  --agent local-automation \
  --message "Check ops queue"

# Clear agent binding
openclaw cron edit <job-id> --clear-agent
```

### Feature 6: Session Key Routing

```bash
openclaw cron add \
  --name "routed-job" \
  --cron "0 9 * * *" \
  --session isolated \
  --session-key "agent:main:daily-tasks" \
  --message "Morning routine"
```

---

## 6. Working Configuration Examples

### Example 1: Completely Silent Background Job

```bash
openclaw cron add \
  --name "silent-monitor" \
  --description "Silent system monitoring - no notifications" \
  --cron "*/15 * * * *" \
  --session isolated \
  --message "Check disk space, memory, and services. Log results to file. Do not send any messages." \
  --no-deliver \
  --timeout-seconds 60 \
  --light-context
```

### Example 2: Silent Job with Local Model

```bash
openclaw cron add \
  --name "local-analysis" \
  --description "Run local LLM analysis silently" \
  --cron "0 */4 * * *" \
  --session isolated \
  --agent local-automation \
  --model "ollama/qwen2.5:14b" \
  --message "Analyze recent logs and update local database. No output needed." \
  --no-deliver \
  --timeout-seconds 180
```

### Example 3: Daily Summary with Delivery

```bash
openclaw cron add \
  --name "daily-summary" \
  --description "Daily morning summary to Telegram" \
  --cron "0 7 * * *" \
  --tz "Europe/Dublin" \
  --session isolated \
  --message "Generate daily summary: weather, calendar, tasks" \
  --announce \
  --channel telegram \
  --to "8378714141"
```

### Example 4: Main Session Reminder

```bash
openclaw cron add \
  --name "standup-reminder" \
  --description "Remind about daily standup" \
  --at "9:00" \
  --session main \
  --system-event "Daily standup starts in 30 minutes" \
  --wake now \
  --delete-after-run
```

### Example 5: JSON Jobs File Configuration

```json
{
  "version": 1,
  "jobs": [
    {
      "id": "silent-monitor",
      "agentId": "main",
      "name": "silent-monitor",
      "enabled": true,
      "schedule": {
        "kind": "cron",
        "expr": "*/15 * * * *"
      },
      "sessionTarget": "isolated",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "Check system status silently"
      },
      "delivery": {
        "mode": "none"
      }
    },
    {
      "id": "daily-brief",
      "agentId": "main",
      "name": "daily-brief",
      "enabled": true,
      "schedule": {
        "kind": "cron",
        "expr": "0 7 * * *",
        "tz": "Europe/Dublin"
      },
      "sessionTarget": "isolated",
      "wakeMode": "now",
      "payload": {
        "kind": "agentTurn",
        "message": "Generate daily briefing"
      },
      "delivery": {
        "mode": "announce",
        "channel": "telegram",
        "to": "8378714141"
      }
    }
  ]
}
```

---

## 7. Migration Guide: Silencing Existing Jobs

### To Silence an Existing Job:

```bash
# Option 1: Edit to use --no-deliver
openclaw cron edit <job-id> --no-deliver

# Option 2: Disable delivery (same effect)
openclaw cron edit <job-id> --no-best-effort-deliver
```

### To Check Current Job Configuration:

```bash
openclaw cron list --json
openclaw cron runs --id <job-id> --limit 10
```

---

## 8. Troubleshooting Silent Jobs

### Job Not Running Silently?

1. **Check delivery mode:**
   ```bash
   openclaw cron list --json | findstr "delivery"
   ```

2. **Verify session target:**
   - `isolated` jobs need explicit `delivery.mode: "none"` to be silent
   - `main` jobs are silent by default (no announce)

3. **Check for legacy notify field:**
   - Old jobs with `notify: true` may still announce
   - Edit to use new `delivery` object

### Job Still Announcing?

If a job is still announcing despite `--no-deliver`:

1. Check if it's an isolated job with default delivery:
   ```bash
   openclaw cron edit <job-id> --no-deliver
   ```

2. For JSON editing, ensure the `delivery` object is set:
   ```json
   "delivery": { "mode": "none" }
   ```

---

## 9. Key Takeaways

1. **`wakeMode` is NOT deprecated** - it controls timing of main-session summaries
2. **Use `--no-deliver`** to completely silence isolated cron jobs
3. **Main session jobs are silent by default** - they only add context to heartbeats
4. **The `delivery` object** provides granular control over notifications
5. **2026.3.1 adds** failure alerts, thinking control, and lightweight context options

---

## References

- OpenClaw Documentation: https://docs.openclaw.ai/automation/cron-jobs
- Cron vs Heartbeat: https://docs.openclaw.ai/automation/cron-vs-heartbeat
- Configuration Reference: https://docs.openclaw.ai/gateway/configuration-reference
- CLI Help: `openclaw cron --help`, `openclaw cron add --help`, `openclaw cron edit --help`

---

*Research completed by subagent on 2026-03-03*
