# Manual Memory Management System for AI Assistants
## Implementation Plan for Karen

**Research Date:** 2026-03-02  
**Goal:** Build a reliable system for capturing and organizing conversation history without relying on broken automatic logging

---

## Executive Summary

Based on extensive research into AI memory management best practices, this document provides a complete, immediately implementable system for manual memory logging. The approach combines proven techniques from production AI systems with practical file-based organization that works without complex infrastructure.

---

## 1. Best Practices for Manual Memory Logging

### Core Principles (from Industry Research)

**1.1 The Three-Tier Memory Model**

Research shows effective AI memory systems use three distinct layers:

| Layer | Purpose | Retention | Implementation |
|-------|---------|-----------|----------------|
| **Working Memory** | Current conversation context | Session-only | Active context in prompt |
| **Short-term Memory** | Recent conversations (days) | 7-30 days | Daily log files |
| **Long-term Memory** | Curated knowledge, patterns | Permanent | Summarized MEMORY.md |

**1.2 What to Log vs. What to Skip**

**ALWAYS LOG:**
- Decisions made and reasoning
- Important facts about the user (preferences, projects, constraints)
- Patterns discovered ("when X happens, do Y")
- Errors made and lessons learned
- External actions taken (emails sent, files modified)
- URLs, references, resources mentioned

**SKIP LOGGING:**
- Routine greetings and pleasantries
- Redundant confirmations
- Temporary troubleshooting steps that didn't work
- Raw output that can be regenerated

**1.3 The 5-Message Checkpoint Rule**

From production experience: Every 5 messages or at natural breakpoints, explicitly summarize:
- What was established
- What decisions were made
- What context carries forward

This prevents context degradation that occurs around message 7-10 in long conversations.

---

## 2. File Organization Strategy

### 2.1 Directory Structure

```
workspace/
├── memory/
│   ├── daily/                    # Raw daily conversation logs
│   │   ├── 2026-03-02.md
│   │   ├── 2026-03-01.md
│   │   └── ...
│   ├── weekly/                   # Weekly summaries (auto-generated)
│   │   ├── 2026-W09.md
│   │   └── ...
│   ├── topics/                   # Subject-based organization
│   │   ├── projects/
│   │   │   ├── project-alpha.md
│   │   │   └── project-beta.md
│   │   ├── people/
│   │   │   ├── contacts.md
│   │   │   └── relationships.md
│   │   ├── lessons/
│   │   │   └── learned.md
│   │   └── resources/
│   │       ├── tools.md
│   │       └── references.md
│   └── MEMORY.md                 # Master curated memory file
├── logs/                         # System/technical logs (separate)
└── archive/                      # Old daily files (>90 days)
```

### 2.2 Daily Log Format (YYYY-MM-DD.md)

```markdown
# Memory Log: 2026-03-02

## Session Summary
- **Active Projects:** Project Alpha (deadline: 2026-03-15)
- **Context from Previous:** Continuing API integration work
- **Key Decisions Made:** 
  - Switched from REST to GraphQL for data fetching

---

## Conversation 1: [Topic/Project Name]

### Context
[What we were working on, why]

### Key Exchanges
- **User asked:** [paraphrased question/request]
- **I did:** [actions taken]
- **Outcome:** [result, decision, or deliverable]
- **Files Modified:** [list any changes]

### New Information Learned
- User prefers [specific preference]
- [Entity X] is related to [Entity Y] in [specific way]

### Decisions & Commitments
- [Decision made and reasoning]
- [Follow-up needed]

---

## Conversation 2: [Topic]
[Same structure...]

---

## End-of-Day Summary

### Completed Today
- [ ] Task 1
- [x] Task 2

### Carry Forward
- [Pending item for tomorrow]

### Patterns Noticed
- [Any insights about user preferences or workflows]
```

### 2.3 Topic-Based Cross-Referencing

Create topic files that aggregate information across days:

```markdown
# Topic: Project Alpha

## Overview
[One-paragraph project description]

## Key Facts
- Started: 2026-02-15
- Deadline: 2026-03-15
- Tech Stack: Node.js, PostgreSQL, React

## Decisions Log
| Date | Decision | Context | Status |
|------|----------|---------|--------|
| 2026-03-02 | Use GraphQL | Better type safety | Active |
| 2026-02-28 | PostgreSQL over Mongo | ACID requirements | Active |

## Related Conversations
- [2026-03-02](../daily/2026-03-02.md) - API design decisions
- [2026-02-28](../daily/2026-02-28.md) - Database selection

## Open Questions
- [ ] How to handle authentication?
```

---

## 3. Search and Retrieval System

### 3.1 Tools Required

**Windows/PowerShell Setup:**

```powershell
# Install ripgrep (rg) - fastest text searcher
winget install BurntSushi.ripgrep.MSVC

# Install fzf - fuzzy finder (optional but powerful)
winget install junegunn.fzf
```

**Basic Search Commands:**

```powershell
# Search all memory files for keyword
rg "Project Alpha" memory/

# Search with context (3 lines before/after)
rg -C 3 "deadline" memory/daily/

# Search only in headers
rg "^# " memory/daily/2026-03-02.md

# Search by date range
rg "2026-03" memory/daily/

# Find files mentioning specific person
rg -l "John Smith" memory/

# Search in topic files only
rg "decision" memory/topics/
```

### 3.2 Search Index Strategy

Create a simple index file for quick lookups:

```markdown
# Memory Index

## People
- John Smith: memory/topics/people/contacts.md
- Jane Doe: memory/daily/2026-03-01.md (line 45)

## Projects
- Project Alpha: memory/topics/projects/project-alpha.md
- Project Beta: memory/daily/2026-02-28.md

## Key Decisions
- GraphQL adoption: memory/daily/2026-03-02.md
- Database choice: memory/topics/projects/project-alpha.md

## Resources
- API Documentation: memory/topics/resources/tools.md
```

### 3.3 Weekly Review Process

Every week, run this search audit:

```powershell
# Find all decisions made this week
rg "^### Decisions" memory/daily/2026-W09*

# Find all new contacts mentioned
rg -i "contact|met with|spoke to" memory/daily/2026-W09*

# Find unresolved items
rg -i "TODO|FIXME|pending|follow.up" memory/daily/
```

---

## 4. Automated Summarization Techniques

### 4.1 Manual Summarization Workflow

Since we can't rely on automatic logging, use this structured approach:

**During Conversation (Lightweight Notes):**
```
[Scratchpad - quick bullet points]
- User wants X
- Decided on Y approach
- Need to check Z
```

**End of Conversation (Structured Log):**
Expand scratchpad into full format above.

**End of Day (Daily Summary):**
Review all conversations, update MEMORY.md with distilled learnings.

### 4.2 The SUMMARIZE Prompt Template

When you need to condense a long conversation, use this structure:

```
Summarize this conversation for memory storage:

1. CONTEXT: What were we working on?
2. INPUTS: What information did the user provide?
3. ACTIONS: What did I do?
4. OUTPUTS: What was delivered?
5. DECISIONS: What was decided and why?
6. LEARNINGS: What new information about the user/preferences?
7. FOLLOW-UP: What remains to be done?

Format as bullet points, max 200 words.
```

### 4.3 Recursive Summarization (for Long-Term Memory)

When MEMORY.md grows too large (>500 lines):

1. **Archive old entries** to `memory/archive/YYYY-MM.md`
2. **Extract timeless lessons** to `memory/topics/lessons/learned.md`
3. **Keep only active context** in MEMORY.md
4. **Maintain links** between archived and current content

---

## 5. Building a Memory Stack That Grows

### 5.1 The Memory Stack Architecture

Think of memory as a stack that gets compressed as it ages:

```
[Working Memory]      <- Current conversation (immediate)
       |
       v
[Daily Logs]          <- Raw transcripts (7-30 days)
       |
       v
[Weekly Summaries]    <- Compressed week view (4-12 weeks)
       |
       v
[Topic Files]         <- Subject-organized knowledge (ongoing)
       |
       v
[MEMORY.md]           <- Curated long-term memory (permanent)
       |
       v
[Archive]             <- Historical reference (as needed)
```

### 5.2 Growth Rules

**Daily Layer:**
- Keep 30 days of daily files
- After 30 days, summarize and archive

**Weekly Layer:**
- Generate automatically from daily files
- Keep 12 weeks (3 months)
- After 3 months, fold into topic files

**Topic Layer:**
- Continuously updated
- Link to specific daily entries
- Prune outdated information quarterly

**MEMORY.md:**
- Maximum 500 lines
- Only curated, timeless information
- Review and compress monthly

### 5.3 The Compression Pipeline

```
Daily (Raw) → Weekly (Summarized) → Monthly (Thematic) → Yearly (Archive)
    ↓              ↓                    ↓                  ↓
  100% detail    50% detail          20% detail         5% detail
  100% volume    25% volume          10% volume         2% volume
```

---

## 6. Implementation Checklist

### Week 1: Foundation
- [ ] Create directory structure
- [ ] Set up ripgrep
- [ ] Create template files
- [ ] Write first daily log
- [ ] Create initial MEMORY.md

### Week 2: Habit Formation
- [ ] Log every conversation (even brief ones)
- [ ] End-of-day summary routine
- [ ] Test search commands
- [ ] Create first topic file

### Week 3: Optimization
- [ ] Review search patterns
- [ ] Refine templates based on usage
- [ ] Create index file
- [ ] Set up weekly review reminder

### Week 4: Maintenance
- [ ] First weekly summary
- [ ] Archive old daily files
- [ ] Update MEMORY.md with distilled learnings
- [ ] Document any process improvements

---

## 7. Quick Reference: Memory Commands

### PowerShell Aliases (add to $PROFILE)

```powershell
# Quick memory search
function mm { rg $args memory/ }

# Today's memory file
function today { code memory/daily/(Get-Date -Format "yyyy-MM-dd").md }

# Yesterday's memory
function yesterday { 
    $yesterday = (Get-Date).AddDays(-1).ToString("yyyy-MM-dd")
    code memory/daily/$yesterday.md 
}

# Search for decisions
function decisions { rg -i "decision|decided" memory/ }

# Find TODOs
function todos { rg -i "TODO|FIXME|pending" memory/ }
```

### Daily Routine (5 minutes)

1. **During conversations:** Quick scratchpad notes
2. **End of conversation:** Expand to structured format
3. **End of day:** 
   - Review day's logs
   - Update MEMORY.md with key learnings
   - Note any follow-ups for tomorrow

### Weekly Routine (15 minutes)

1. Review all daily files from the week
2. Create weekly summary
3. Update topic files with new information
4. Archive daily files older than 30 days
5. Compress MEMORY.md if needed

---

## 8. Troubleshooting Common Issues

| Problem | Solution |
|---------|----------|
| Forgetting to log | Set a 30-min reminder; log at natural breakpoints |
| Logs too verbose | Use the "What to Log" filter; be ruthless |
| Can't find old info | Improve index file; use more specific search terms |
| MEMORY.md too long | Archive old entries; extract to topic files |
| Duplicate information | Cross-reference with links; use single source of truth |
| Outdated info | Quarterly review; mark stale entries with [DEPRECATED] |

---

## 9. Advanced Techniques

### 9.1 Entity Registry Pattern

From the research: Maintain a JSON/CSV file for tracking people, projects, and entities:

```json
{
  "entities": [
    {
      "id": "proj-alpha",
      "name": "Project Alpha",
      "type": "project",
      "status": "active",
      "first_seen": "2026-02-15",
      "last_mentioned": "2026-03-02",
      "related": ["person-john", "tech-graphql"],
      "file": "memory/topics/projects/project-alpha.md"
    }
  ]
}
```

### 9.2 Conversation Linking

Always link related conversations:
```markdown
## Related
- Previous: [2026-03-01](memory/daily/2026-03-01.md#project-alpha)
- Next: [2026-03-03](memory/daily/2026-03-03.md)
- Topic: [Project Alpha](memory/topics/projects/project-alpha.md)
```

### 9.3 Confidence Scoring

Mark memory reliability:
- **[CONFIRMED]** - Verified information
- **[INFERRED]** - Reasonable assumption
- **[TEMP]** - May change, don't rely on it

---

## Summary

This system provides:

1. **Immediate capture** via daily logs
2. **Organized retrieval** via topic files and search
3. **Long-term persistence** via MEMORY.md
4. **Scalable growth** via compression pipeline
5. **No external dependencies** - works with just text files and ripgrep

The key insight from research: **Manual memory management beats broken automatic logging** because it forces intentionality. You remember what you choose to remember, which is exactly what matters.

---

*Implementation can begin immediately. Start with the directory structure and first daily log.*
