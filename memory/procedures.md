# Procedures — How I Do Things

_Last updated: 2026-04-07_

---

## 🎨 Communication Preferences
- Language: English
- Style: Concise when needed, thorough when it matters
- No corporate speak or performative helpfulness
- Actions over words

## 🔧 Tool Workflows

### Research Automation
- Use Kimi k2.5 subagent for web research
- Timeout: 300s for research tasks
- Store results in memory/YYYY-MM-DD.md

### System Checks
- Hourly Ollama-based checks for system status
- Daily memory logging triggered by cron
- Security audits: 4 critical, 5 warn, 1 info (known issues, home use acceptable)

### GitHub Backup
- Daily at 2 AM
- Commits all workspace changes
- Pushes to remote repository

## 📝 Format Preferences
- Tables for comparisons
- Bullet lists for Discord
- Code blocks for technical details

## ⚡ Shortcuts & Patterns
- "backup" → triggers GitHub backup workflow
- "TRIGGER-RESEARCH-{topic}" → spawns research subagent
- "DAILY-SESSION-CLEANUP" → archives old sessions
- "ARCHIVE-SESSIONS" → session archival at 22:55 daily

## ⚠️ Known Issues
- Ollama + local-automation agent: Use agent:main instead due to sandbox isolation
- llama3.2:3b tool calling: Outputs tools in content instead of tool_calls - avoid using

<!-- consolidated -->
