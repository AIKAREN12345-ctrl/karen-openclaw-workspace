# Skill Setup Status - 2026-03-31

## ✅ Completed

### Obsidian Skill
- **Status:** Installed successfully
- **Location:** `~/.openclaw/workspace/skills/obsidian/`
- **Skill file:** SKILL.md ready

### What Obsidian Skill Enables:
- Read/search your Obsidian vault notes
- Create new notes programmatically
- Move/rename notes with link updates
- Search content inside notes
- Print note paths for automation

## ⏳ Pending: CLI Installation

The Obsidian skill requires `obsidian-cli` (now called `notesmd-cli`) to be installed.

### Installation Options:

**Option 1: Manual Download (Windows)**
1. Download: https://github.com/Yakitrak/notesmd-cli/releases/download/v0.3.4/notesmd-cli_windows_amd64.exe
2. Rename to `obsidian-cli.exe` (for skill compatibility)
3. Add to PATH or place in `C:\Windows\System32\`

**Option 2: Build from Source (requires Go)**
```bash
go install github.com/Yakitrak/notesmd-cli@latest
```

**Option 3: Use Obsidian URI Directly**
The skill can also work with Obsidian's native URI scheme without CLI:
- `obsidian://open?vault=MyVault&file=NoteName`
- Limited functionality vs full CLI

## ❌ Coding Agent Skill

**Status:** Not found in ClawHub

**Alternative:** The `coding-agent` skill may have been renamed or removed. Current alternatives:
- Use `sessions_spawn` with `runtime: "acp"` for Codex/Claude Code
- Built-in ACP support via `sessions_spawn` tool

## Next Steps

1. **Install obsidian-cli** using one of the methods above
2. **Set default vault:** `obsidian-cli set-default "YourVaultName"`
3. **Test:** I can then read/create/search your Obsidian notes
4. **For coding:** Use `sessions_spawn` with ACP runtime instead

## Documentation

- Obsidian skill: `~/.openclaw/workspace/skills/obsidian/SKILL.md`
- notesmd-cli repo: https://github.com/Yakitrak/notesmd-cli
