# Learnings Log

## [LRN-20260403-001] OpenClaw version management

**Logged**: 2026-04-03T20:46:00Z
**Priority**: high
**Status**: promoted
**Area**: config

### Summary
Always test thoroughly after OpenClaw updates. Major versions (2026.3.x → 2026.4.x) can break core functionality.

### Details
- 2026.4.1 introduced security hardening that broke exec tool
- No configuration workaround available
- Downgrade was only solution
- Cost: 2+ hours debugging, multiple restarts

### Suggested Action
1. Pin OpenClaw version in documentation
2. Test critical tools (exec, browser, memory) after updates
3. Keep rollback plan ready
4. Check GitHub issues before upgrading

### Metadata
- Source: error
- Related Files: AGENTS.md
- Promoted: AGENTS.md (added version management section)

---

## [LRN-20260403-002] Skill installation workflow

**Logged**: 2026-04-03T20:46:00Z
**Priority**: medium
**Status**: pending
**Area**: workflow

### Summary
Skills can be installed by downloading SKILL.md files directly from GitHub/clawhub to workspace/skills/ directory.

### Details
- ClawHub CLI blocked by exec issue
- Direct download via web_fetch works
- Skills become available immediately
- No restart required

### Suggested Action
Document this workflow for future skill installs.

### Metadata
- Source: best_practice
- Related Files: skills/*/SKILL.md

---
