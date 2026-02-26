# OPENCLAW SKILLS REVIEW - Complete Analysis

**Review Date:** 2026-02-25
**System:** Karen on Windows 11 (DESKTOP-M8AO8LN)
**Current Setup:** Telegram, VNC, Browser automation, Local LLMs

---

## 🎯 EXECUTIVE SUMMARY

**Total Skills:** 51
**Ready to Use:** 3
**Missing (Installable):** 48

**Top Recommendations for Our Setup:**
1. **coding-agent** - Essential for development work
2. **github** - Critical for our research/documentation workflow
3. **session-logs** - Helpful for debugging my memory issues
4. **sag** - ElevenLabs TTS for voice output
5. **clawhub** - Skill management

---

## ✅ READY TO USE (3 Skills)

### 1. healthcheck ⭐⭐⭐⭐⭐
**Status:** Ready | **Priority:** HIGH

**What it does:**
- Security audits and hardening
- Firewall/SSH configuration
- Risk posture assessment
- Periodic security checks via cron

**Usefulness to us:**
- ✅ Already using this (system security)
- ✅ Automated security monitoring
- ✅ Perfect for our "trusted but verified" approach

**Verdict:** KEEP USING

---

### 2. skill-creator ⭐⭐⭐⭐⭐
**Status:** Ready | **Priority:** HIGH

**What it does:**
- Create custom AgentSkills
- Package skills with scripts and assets
- Update existing skills

**Usefulness to us:**
- ✅ Essential for extending capabilities
- ✅ Could create custom VNC control skill
- ✅ Package our automation scripts as skills

**Verdict:** USE TO CREATE CUSTOM SKILLS

---

### 3. weather ⭐⭐⭐
**Status:** Ready | **Priority:** LOW

**What it does:**
- Weather forecasts via wttr.in or Open-Meteo
- Current conditions, temperature
- No API key needed

**Usefulness to us:**
- ⚠️ Nice to have but not essential
- Could add to morning briefings
- Low priority given our automation focus

**Verdict:** NICE-TO-HAVE, NOT ESSENTIAL

---

## ❌ MISSING SKILLS - DETAILED REVIEWS

### DEVELOPMENT & CODING

#### 4. coding-agent ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** CRITICAL

**What it does:**
- Delegate coding to Codex, Claude Code, or Pi agents
- Background process execution
- File exploration and iterative coding
- PR review and implementation

**Use Cases:**
- Building new features
- Refactoring large codebases
- Code review automation
- Complex multi-file changes

**Usefulness to us:**
- ✅ PERFECT for our automation scripts
- ✅ Could handle complex VNC control implementations
- ✅ Background coding while we do other things
- ✅ Handles file exploration automatically

**Blockers:**
- Requires bash tool with pty:true (we have exec)
- Cannot use in ~/clawd workspace (we use ~/.openclaw/workspace)

**Verdict:** INSTALL IMMEDIATELY - Game changer for development

---

#### 5. github ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** CRITICAL

**What it does:**
- GitHub CLI operations (gh)
- Issues, PRs, CI runs
- Code review
- API queries

**Use Cases:**
- Check PR status
- Create/comment on issues
- List/filter PRs and issues
- View CI run logs

**Usefulness to us:**
- ✅ PERFECT for our documentation workflow
- ✅ Could automate GitHub issue tracking
- ✅ Monitor OpenClaw GitHub for updates
- ✅ Track our own project issues

**Blockers:**
- Requires gh auth configuration
- Cannot do complex web UI flows (we have browser for that)

**Verdict:** INSTALL - Essential for GitHub integration

---

#### 6. gh-issues ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** HIGH

**What it does:**
- Fetch GitHub issues
- Spawn sub-agents to implement fixes
- Open PRs automatically
- Monitor PR review comments
- Address feedback automatically

**Use Cases:**
- Automated bug fixing
- Issue triage and implementation
- PR review automation
- Continuous monitoring

**Usefulness to us:**
- ✅ Could track OpenClaw issues automatically
- ✅ Implement fixes for known bugs
- ✅ Monitor our own project issues
- ⚠️ Sub-agent spawning has issues with Ollama (but works with cloud models)

**Verdict:** INSTALL - Powerful for automation, but note sub-agent limitations

---

### COMMUNICATION & MESSAGING

#### 7. himalaya ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM-HIGH

**What it does:**
- Email CLI (IMAP/SMTP)
- List, read, write, reply, forward emails
- Search and organize
- Multiple account support
- MML (MIME Meta Language) composition

**Use Cases:**
- Automated email responses
- Email monitoring
- Newsletter management
- Email-based workflows

**Usefulness to us:**
- ✅ Could complete our email automation
- ✅ Send automated reports
- ✅ Monitor inbox for triggers
- ⚠️ We have partial email setup (send-only scripts)

**Blockers:**
- Requires IMAP/SMTP configuration
- May conflict with existing email scripts

**Verdict:** INSTALL - Complete email solution

---

#### 8. slack ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Slack control via message tool
- React to messages
- Pin/unpin items
- Channel and DM operations

**Use Cases:**
- Slack notifications
- Automated responses
- Channel management

**Usefulness to us:**
- ⚠️ We use Telegram, not Slack
- Would need Slack workspace
- Nice for team integration but not essential

**Verdict:** SKIP - We don't use Slack

---

#### 9. discord ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Discord operations via message tool

**Use Cases:**
- Discord notifications
- Server management

**Usefulness to us:**
- ⚠️ We use Telegram
- No Discord integration needed

**Verdict:** SKIP - Not needed

---

#### 10. imsg ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- iMessage/SMS CLI
- List chats, history
- Send messages via Messages.app

**Use Cases:**
- iMessage automation
- SMS notifications

**Usefulness to us:**
- ⚠️ macOS only (we're on Windows)
- Not applicable

**Verdict:** SKIP - macOS only

---

#### 11. bluebubbles ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- iMessage via BlueBubbles
- Send/manage iMessages

**Use Cases:**
- iMessage on non-Apple devices

**Usefulness to us:**
- ⚠️ iMessage focused
- We use Telegram

**Verdict:** SKIP - Not needed

---

#### 12. wacli ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- WhatsApp CLI
- Send messages
- Search/sync history

**Use Cases:**
- WhatsApp automation

**Usefulness to us:**
- ⚠️ We use Telegram
- Different platform

**Verdict:** SKIP - Not needed

---

### PRODUCTIVITY & NOTES

#### 13. notion ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Notion API integration
- Create/manage pages
- Database operations
- Block manipulation

**Use Cases:**
- Knowledge base
- Project management
- Documentation

**Usefulness to us:**
- ⚠️ We use markdown files in workspace
- Would require Notion account
- Nice but not essential given our file-based approach

**Verdict:** OPTIONAL - Nice but we have working system

---

#### 14. obsidian ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Obsidian vault management
- Plain Markdown notes
- Automation via obsidian-cli

**Use Cases:**
- Note taking
- Knowledge management
- Zettelkasten method

**Usefulness to us:**
- ⚠️ We use markdown files already
- Similar to our current setup
- Could migrate but not necessary

**Verdict:** OPTIONAL - We have working markdown system

---

#### 15. bear-notes ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Bear notes via grizzly CLI
- Create, search, manage

**Use Cases:**
- Note taking (macOS)

**Usefulness to us:**
- ⚠️ macOS only
- Not applicable

**Verdict:** SKIP - macOS only

---

#### 16. apple-notes ⭐⭐
**Status:** Missing | **Priority:** NONE

**What it does:**
- Apple Notes via memo CLI
- Create, view, edit, delete

**Usefulness to us:**
- ❌ macOS only
- Not applicable

**Verdict:** SKIP

---

#### 17. apple-reminders ⭐⭐
**Status:** Missing | **Priority:** NONE

**What it does:**
- Apple Reminders via remindctl

**Usefulness to us:**
- ❌ macOS only
- Not applicable

**Verdict:** SKIP

---

#### 18. things-mac ⭐⭐
**Status:** Missing | **Priority:** NONE

**What it does:**
- Things 3 task management

**Usefulness to us:**
- ❌ macOS only
- Not applicable

**Verdict:** SKIP

---

### MEDIA & ENTERTAINMENT

#### 19. spotify-player ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Terminal Spotify control
- Playback, search
- spogo or spotify_player CLI

**Use Cases:**
- Music control
- Playlist management

**Usefulness to us:**
- ⚠️ Nice but not essential
- Entertainment vs productivity

**Verdict:** SKIP - Not essential for our setup

---

#### 20. sonoscli ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Sonos speaker control
- Discover, play, volume, group

**Usefulness to us:**
- ⚠️ Requires Sonos speakers
- Not essential

**Verdict:** SKIP

---

#### 21. blucli ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- BluOS speaker control

**Usefulness to us:**
- ⚠️ Requires BluOS devices
- Not essential

**Verdict:** SKIP

---

#### 22. openai-whisper ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Local speech-to-text
- No API key needed
- Whisper CLI

**Use Cases:**
- Audio transcription
- Voice notes to text
- Meeting transcription

**Usefulness to us:**
- ✅ Could transcribe voice messages
- ✅ Local processing (privacy)
- ⚠️ Requires audio input setup

**Verdict:** CONSIDER - Useful for voice workflows

---

#### 23. openai-whisper-api ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Cloud-based Whisper transcription
- OpenAI API

**Usefulness to us:**
- ⚠️ Cloud-based (costs tokens)
- Local version preferred

**Verdict:** SKIP - Use local whisper instead

---

#### 24. sag ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** HIGH

**What it does:**
- ElevenLabs text-to-speech
- mac-style "say" UX
- High quality voices

**Use Cases:**
- Voice responses
- Audio notifications
- Accessibility

**Usefulness to us:**
- ✅ PERFECT for voice storytelling
- ✅ "Storytime" mode for summaries
- ✅ More engaging than text
- ⚠️ Requires ElevenLabs API key

**Verdict:** INSTALL - Great for user experience

---

#### 25. sherpa-onnx-tts ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Local text-to-speech
- Offline, no cloud
- sherpa-onnx engine

**Use Cases:**
- Voice output without API costs
- Privacy-preserving TTS

**Usefulness to us:**
- ✅ Local processing
- ✅ No API costs
- ⚠️ Lower quality than ElevenLabs

**Verdict:** CONSIDER - Alternative to sag if no API key

---

#### 26. songsee ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Audio spectrograms
- Feature visualization

**Usefulness to us:**
- ⚠️ Niche audio analysis
- Not essential

**Verdict:** SKIP

---

#### 27. video-frames ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Extract frames from videos
- Short clips using ffmpeg

**Use Cases:**
- Video analysis
- Thumbnail extraction
- Frame sampling

**Usefulness to us:**
- ✅ Could analyze video content
- ✅ Works with VNC recordings
- ⚠️ Requires ffmpeg

**Verdict:** CONSIDER - Useful for video workflows

---

#### 28. openai-image-gen ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Batch image generation
- OpenAI Images API
- Gallery generation

**Usefulness to us:**
- ⚠️ API costs
- Not essential for our workflow

**Verdict:** SKIP - Not needed

---

#### 29. nano-banana-pro ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Image generation via Gemini 3 Pro

**Usefulness to us:**
- ⚠️ Image generation not essential

**Verdict:** SKIP

---

#### 30. camsnap ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- RTSP/ONVIF camera capture
- Frames and clips

**Use Cases:**
- Security camera monitoring
- Visual verification

**Usefulness to us:**
- ✅ Could complement VNC
- ✅ Security camera integration
- ⚠️ Requires camera setup

**Verdict:** CONSIDER - If we add cameras

---

### AI & AUTOMATION

#### 31. gemini ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM-HIGH

**What it does:**
- Gemini CLI
- One-shot Q&A
- Summaries
- Generation

**Use Cases:**
- Quick questions
- Alternative to web search
- Different AI perspective

**Usefulness to us:**
- ✅ Alternative AI model
- ✅ Different capabilities than Kimi
- ✅ Free tier available

**Verdict:** INSTALL - Good AI alternative

---

#### 32. summarize ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM-HIGH

**What it does:**
- Summarize URLs
- Podcast transcription
- Local file text extraction

**Use Cases:**
- Article summaries
- Video transcripts
- Document extraction

**Usefulness to us:**
- ✅ PERFECT for research
- ✅ Could summarize web pages
- ✅ YouTube/video transcripts

**Verdict:** INSTALL - Great for research workflow

---

#### 33. oracle ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Prompt + file bundling
- Engine management
- Sessions
- File attachment patterns

**Usefulness to us:**
- ⚠️ Advanced prompt engineering
- Not essential for current workflow

**Verdict:** OPTIONAL

---

#### 34. nano-pdf ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- PDF editing with natural language
- nano-pdf CLI

**Use Cases:**
- PDF modifications
- Document processing

**Usefulness to us:**
- ✅ Could process PDFs
- ⚠️ We don't work with PDFs much

**Verdict:** OPTIONAL

---

#### 35. model-usage ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- CodexBar CLI cost tracking
- Per-model usage summary

**Usefulness to us:**
- ⚠️ For Codex/Claude usage tracking
- We use Kimi primarily

**Verdict:** SKIP - Not applicable

---

### MONITORING & LOGGING

#### 36. session-logs ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** HIGH

**What it does:**
- Search session logs
- Analyze conversations
- jq-based queries

**Use Cases:**
- Find past conversations
- Debug issues
- Pattern analysis

**Usefulness to us:**
- ✅ PERFECT for my memory issues
- ✅ Could search what we did before
- ✅ Debug why things failed
- ✅ Find previous solutions

**Verdict:** INSTALL - Essential for memory/debugging

---

#### 37. blogwatcher ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- RSS/Atom feed monitoring
- Blog update tracking

**Use Cases:**
- News monitoring
- Blog following
- Update notifications

**Usefulness to us:**
- ✅ Could monitor AI news
- ✅ Track OpenClaw updates
- ⚠️ We have ai-news-monitor script

**Verdict:** CONSIDER - Alternative to our script

---

### SMART HOME

#### 38. openhue ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Philips Hue light control
- Scenes and automation

**Usefulness to us:**
- ⚠️ Requires Hue lights
- Not essential

**Verdict:** SKIP

---

#### 39. eightctl ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Eight Sleep pod control
- Temperature, alarms

**Usefulness to us:**
- ⚠️ Requires Eight Sleep device
- Not essential

**Verdict:** SKIP

---

### SECURITY & PASSWORDS

#### 40. 1password ⭐⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM-HIGH

**What it does:**
- 1Password CLI (op)
- Secret injection
- Multi-account support
- Desktop app integration

**Use Cases:**
- Secure credential management
- Secret injection in scripts
- Password automation

**Usefulness to us:**
- ✅ Better than env vars for secrets
- ✅ Secure credential storage
- ✅ VNC password, API keys
- ⚠️ Requires 1Password account

**Verdict:** CONSIDER - Better security for credentials

---

### PLATFORM-SPECIFIC (macOS)

#### 41. peekaboo ⭐⭐
**Status:** Missing | **Priority:** NONE

**What it does:**
- macOS UI automation
- Capture and automation

**Usefulness to us:**
- ❌ macOS only
- Not applicable

**Verdict:** SKIP

---

### MESSAGING & SOCIAL

#### 42. xurl (Twitter/X) ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- X/Twitter API CLI
- Post, reply, search
- DMs, media upload

**Usefulness to us:**
- ⚠️ Social media not our focus
- Would need X account

**Verdict:** SKIP

---

#### 43. gog ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Google Workspace CLI
- Gmail, Calendar, Drive

**Usefulness to us:**
- ⚠️ We use Microsoft/Windows ecosystem
- Not essential

**Verdict:** SKIP

---

### PROJECT MANAGEMENT

#### 44. trello ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Trello board management
- Cards, lists

**Usefulness to us:**
- ⚠️ We use files/markdown
- Not essential

**Verdict:** SKIP

---

### TERMINAL & SESSIONS

#### 45. tmux ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- Remote tmux control
- Send keystrokes
- Scrape pane output

**Use Cases:**
- Long-running sessions
- Remote CLI management

**Usefulness to us:**
- ✅ Could manage background processes
- ✅ Persistent sessions
- ⚠️ We have Windows, not Linux

**Verdict:** OPTIONAL - Windows has different session management

---

### UTILITIES

#### 46. gifgrep ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- GIF search
- Download and extract

**Usefulness to us:**
- ⚠️ Not essential
- Entertainment

**Verdict:** SKIP

---

#### 47. ordercli ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Foodora order checking
- Food delivery status

**Usefulness to us:**
- ⚠️ Not essential
- Personal use

**Verdict:** SKIP

---

#### 48. goplaces ⭐⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Google Places API
- Place search, details

**Usefulness to us:**
- ⚠️ Location services not essential

**Verdict:** SKIP

---

#### 49. mcporter ⭐⭐⭐
**Status:** Missing | **Priority:** MEDIUM

**What it does:**
- MCP server management
- Configure, auth, call tools
- HTTP and stdio support

**Use Cases:**
- Model Context Protocol servers
- External tool integration

**Usefulness to us:**
- ✅ Advanced integration capability
- ⚠️ Complex setup
- Future-proofing

**Verdict:** CONSIDER - For advanced integrations

---

#### 50. voice-call ⭐⭐
**Status:** Missing | **Priority:** LOW

**What it does:**
- Voice call initiation
- OpenClaw voice-call plugin

**Usefulness to us:**
- ⚠️ Not essential
- We use Telegram text

**Verdict:** SKIP

---

#### 51. clawhub ⭐⭐⭐⭐⭐
**Status:** Missing | **Priority:** CRITICAL

**What it does:**
- Search skills on clawhub.com
- Install/update skills
- Publish new skills
- Sync to latest versions

**Use Cases:**
- Skill discovery
- Skill management
- Community sharing

**Usefulness to us:**
- ✅ ESSENTIAL for skill management
- ✅ Find new capabilities
- ✅ Update existing skills
- ✅ Install everything on this list

**Verdict:** INSTALL IMMEDIATELY - Required for skill management

---

## 📊 PRIORITY SUMMARY

### INSTALL IMMEDIATELY (5 skills)
| Skill | Why |
|-------|-----|
| **clawhub** | Required to install other skills |
| **coding-agent** | Essential for development |
| **github** | Critical for GitHub workflow |
| **gh-issues** | Automated issue tracking |
| **session-logs** | Debug memory issues |

### INSTALL SOON (5 skills)
| Skill | Why |
|-------|-----|
| **himalaya** | Complete email solution |
| **sag** | ElevenLabs TTS for voice |
| **gemini** | Alternative AI model |
| **summarize** | Research assistance |
| **1password** | Better credential security |

### CONSIDER (6 skills)
| Skill | Why |
|-------|-----|
| **video-frames** | Video analysis |
| **openai-whisper** | Local transcription |
| **sherpa-onnx-tts** | Free TTS alternative |
| **camsnap** | Camera integration |
| **blogwatcher** | News monitoring |
| **mcporter** | Advanced integrations |

### SKIP (35 skills)
- Platform-specific (macOS only): 5 skills
- Not our ecosystem: 8 skills
- Not essential: 22 skills

---

## 🎯 RECOMMENDED INSTALLATION ORDER

```bash
# 1. Install clawhub first (required for others)
npx clawhub

# 2. Core development skills
openclaw skill install clawhub
openclaw skill install coding-agent
openclaw skill install github
openclaw skill install gh-issues
openclaw skill install session-logs

# 3. Communication & productivity
openclaw skill install himalaya
openclaw skill install sag

# 4. AI & research
openclaw skill install gemini
openclaw skill install summarize

# 5. Security
openclaw skill install 1password
```

---

## 💡 FINAL RECOMMENDATIONS

**Immediate (Today):**
1. Install **clawhub** - Required for everything else
2. Install **coding-agent** - Will transform development workflow
3. Install **github** - Essential for our documentation

**This Week:**
4. Install **himalaya** - Complete email automation
5. Install **sag** - Voice output capability
6. Install **session-logs** - Debug my memory issues

**Next Sprint:**
7. Install **gemini** - Alternative AI for comparison
8. Install **summarize** - Research acceleration
9. Install **gh-issues** - Automated GitHub monitoring

**Total to Install:** 9 skills (of 51)
**Skip:** 42 skills (not applicable or low priority)

---

*"The right tool for the right job, and knowing when you don't need a tool at all."* 🦞