---
name: proactive_research
description: 24/7 automated research system that tracks topics and avoids duplication
metadata:
  openclaw:
    requires:
      tools: ["sessions_spawn"]
      bins: ["python"]
    tags: ["research", "automation", "proactive", "learning"]
    author: "Karen"
    version: "1.0.0"
---

# Proactive Research System

Automatically researches topics on a rotating schedule, tracks what's been learned, and avoids researching the same information twice.

## How It Works

### Research Topics (Rotating Schedule)

| Topic | Frequency | Priority |
|-------|-----------|----------|
| OpenClaw Updates | Daily | High |
| Security Alerts | Daily | High |
| Local LLM Models | Weekly | Medium |
| AI Tools | Weekly | Medium |
| Memory Systems | Weekly | Medium |
| Windows Optimization | Weekly | Low |
| Telegram Bots | Weekly | Low |

### Rotation Logic

1. **Check tracker** - See what's due for research
2. **Pick highest priority** topic that's overdue
3. **Spawn subagent** to research using duckduckgo-search skill
4. **Save results** to `memory/research/YYYY-MM-DD_topic.md`
5. **Update tracker** - Mark as researched with timestamp
6. **Alert if important** - Notify you of critical findings

## Usage

### Run Research Now
```
/skill proactive_research
```

### Check Research Status
```
/skill proactive_research status
```

### Force Specific Topic
```
/skill proactive_research topic openclaw_updates
```

## Automation

Add to cron for automatic research:

```json5
{
  name: "proactive-research",
  schedule: "0 */4 * * *",  // Every 4 hours
  command: "/skill proactive_research"
}
```

## Output

Research results saved to:
- `memory/research/2026-03-03_openclaw_updates.md`
- `memory/research/2026-03-04_security_alerts.md`
- etc.

## Smart Features

- **No duplication** - Tracks last research date per topic
- **Priority-based** - High priority topics researched first
- **Adaptive** - Won't research same query twice in same period
- **Summarized** - Subagents compile findings, not raw dumps
- **Actionable** - Alerts only on important/critical findings

## Topics Evolve

The system can add new topics over time:
- New technologies you mention
- Areas you show interest in
- Seasonal priorities

Just ask: "Add X to proactive research rotation"
