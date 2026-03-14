---
name: memory_maintenance
description: Automated memory maintenance - extracts important details from daily logs
metadata:
  openclaw:
    requires:
      bins: ["python"]
    tags: ["memory", "maintenance", "automation"]
    author: "Karen"
    version: "1.0.0"
---

# Memory Maintenance Skill

Automatically reviews daily memory logs and extracts important personal details for permanent storage in MEMORY.md.

## Usage

Run this skill daily via cron to maintain long-term memory:

```bash
/skill memory_maintenance
```

Or run the Python script directly:

```bash
python ~/.openclaw/workspace/skills/memory-maintenance/memory_maintenance.py
```

## What It Does

1. **Reads yesterday's memory log** (`memory/YYYY-MM-DD.md`)
2. **Extracts personal details** using pattern matching:
   - Medical information
   - Family details
   - Preferences and likes/dislikes
   - Work context
   - Important dates
   - Living situation
3. **Updates MEMORY.md** with new findings
4. **Preserves privacy** - only extracts relevant personal context

## Patterns Detected

- "Ken mentioned..."
- "You said..."
- Medical/health discussions
- Family references
- Preference statements
- Important dates

## Automation

Add to cron for daily automatic updates:

```json5
{
  name: "memory-maintenance",
  schedule: "0 3 * * *",  // 3 AM daily
  command: "/skill memory_maintenance"
}
```

## Manual Review

You can also ask me to review manually:
- "Review this week's logs and update my profile"
- "What have you learned about me recently?"
- "Update MEMORY.md with important details"
