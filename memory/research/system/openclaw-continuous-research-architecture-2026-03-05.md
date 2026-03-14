# OpenClaw Continuous Research System - Comprehensive Analysis
**Date:** 2026-03-05
**Researcher:** Karen (self-research)

## Executive Summary

After thorough investigation of OpenClaw's cron, subagent, and automation systems, I've identified the optimal architecture for continuous background research. The key insight is that **cron jobs cannot directly spawn subagents** — they can only run shell commands or isolated agent turns. True continuous research requires a hybrid approach.

## Key Findings

### 1. Cron Job Limitations

**What Cron Jobs CAN Do:**
- Run `systemEvent` payloads (shell commands, scripts)
- Run `agentTurn` payloads in isolated sessions (`cron:<jobId>`)
- Execute on schedules (cron expressions, intervals, one-shot)
- Deliver results via announce, webhook, or none

**What Cron Jobs CANNOT Do:**
- Directly call `sessions_spawn` (that's an agent tool)
- Spawn subagents from shell commands (no access to agent tools)
- Maintain persistent state across runs

**Critical Architecture Point:**
```
Cron Job → systemEvent (shell) → ❌ Cannot spawn subagents
Cron Job → agentTurn (isolated) → ❌ No sessions_spawn tool
Main Agent → sessions_spawn → ✅ Can spawn subagents
```

### 2. Subagent System Deep Dive

**Subagent Capabilities:**
- Run in isolated sessions (`agent:<agentId>:subagent:<uuid>`)
- Auto-announce results back to requester on completion
- Support nested spawning (max depth 5, default 1)
- Can use all tools except session tools (by default)

**Subagent Limitations:**
- No `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn` (depth 1)
- Context injection: only `AGENTS.md` + `TOOLS.md` (no `SOUL.md`, `USER.md`, etc.)
- Announce is best-effort (lost if gateway restarts)
- Auto-archive after 60 minutes of inactivity

**Timeout Configuration:**
```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "runTimeoutSeconds": 1800,  // 30 min default
        "maxSpawnDepth": 2,         // Allow orchestrators
        "maxChildrenPerAgent": 5,   // Max concurrent children
        "maxConcurrent": 8          // Global concurrency
      }
    }
  }
}
```

### 3. Thread-Bound Sessions (Not Available on Telegram)

**What They Are:**
- Persistent sessions that stay bound to a thread
- Can receive follow-up messages
- Support `/focus`, `/unfocus`, `/agents` commands
- Require `thread: true` + `mode: "session"`

**Limitation:**
- Only supported on Discord currently
- Telegram does NOT support thread bindings
- Error: "thread=true is unavailable because no channel plugin registered subagent_spawning hooks"

### 4. Isolated Cron Sessions

**How They Work:**
- Run in dedicated session: `cron:<jobId>`
- Fresh session ID each run (no conversation carry-over)
- Prompt prefixed with `[cron:<jobId> <job name>]`
- Can use `agentTurn` with full tool access (except session tools)

**Delivery Modes:**
- `announce`: Deliver to channel + post summary to main session
- `webhook`: POST to URL
- `none`: Internal only, no delivery

### 5. The Research System Problem

**Why Our Initial Approach Failed:**
1. Cron job tried to spawn subagents via Python script
2. Script couldn't access `sessions_spawn` (agent tool)
3. Subagents failed due to complex tasks + timeout issues
4. No mechanism for continuous respawning

**Root Cause:**
- Subagents are designed for parallel task execution, not long-running daemons
- Cron jobs are designed for scheduled commands, not agent orchestration
- Gap: No built-in "respawn on completion" mechanism

## Recommended Architectures

### Architecture A: The Orchestrator Pattern (Most Robust)

**Design:**
```
Main Agent (you + me)
  ↓ sessions_spawn (maxSpawnDepth: 2)
Orchestrator Subagent (depth 1, persistent)
  ↓ sessions_spawn
Worker Subagents (depth 2, task-specific)
  ↓ Write to memory
```

**How It Works:**
1. Spawn orchestrator with `maxSpawnDepth: 2` and no timeout
2. Orchestrator maintains a research queue
3. Every 30 minutes, orchestrator spawns worker for next topic
4. Worker researches, writes to memory, completes
5. Orchestrator waits, then spawns next worker
6. Cycle continues indefinitely

**Pros:**
- True continuous operation
- Centralized queue management
- Workers are simple, focused tasks
- Can handle failures gracefully

**Cons:**
- Requires `maxSpawnDepth: 2` config
- Orchestrator uses RAM continuously
- Complex to debug if issues arise

**Implementation:**
```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "runTimeoutSeconds": 0
      }
    }
  }
}
```

### Architecture B: Cron-Triggered Research (Simpler)

**Design:**
```
Cron Job (every hour)
  ↓ agentTurn (isolated session)
Research Agent
  ↓ Research ONE topic
  ↓ Write to memory
  ↓ Complete
```

**How It Works:**
1. Cron job runs every hour with `agentTurn` payload
2. Isolated agent researches ONE specific topic
3. Agent writes findings to memory file
4. Agent completes, session ends
5. Next hour, new agent spawns for next topic

**Pros:**
- Simple, reliable
- No persistent RAM usage
- Each run is fresh (no state issues)
- Easy to debug (check cron logs)

**Cons:**
- Not truly continuous (hourly gaps)
- No queue management
- Topics must rotate predictably

**Implementation:**
```json
{
  "name": "hourly-research",
  "schedule": { "kind": "cron", "expr": "0 * * * *" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Research [TOPIC] and write to memory/research/[TOPIC]-YYYY-MM-DD.md",
    "model": "ollama/qwen2.5:14b"
  },
  "delivery": { "mode": "none" }
}
```

### Architecture C: Heartbeat-Driven Research (Most Flexible)

**Design:**
```
User Message → Main Agent
  ↓ Check if research due
  ↓ If yes: sessions_spawn research agent
  ↓ Research agent works, writes to memory, announces
```

**How It Works:**
1. When you message me, I check `research-state.json`
2. If last research > 1 hour ago, spawn research agent
3. Research agent works independently
4. Results announced when complete
5. State updated

**Pros:**
- No wasted runs (only research when we're active)
- Can adapt topics based on conversation
- Uses main agent for orchestration
- Simple state management

**Cons:**
- Research only happens when you message me
- Not truly background (requires user activity)
- Main agent context grows with research requests

**Implementation:**
- Track last research time in `memory/research-state.json`
- Check on each heartbeat/user message
- Spawn subagent if needed

### Architecture D: Hybrid System (Recommended)

**Design:**
Combine B + C:
- **Cron job**: Hourly lightweight check (isolated session)
- **Main agent**: When active, can trigger additional research
- **Subagents**: Handle actual research tasks

**How It Works:**
1. Cron job hourly: Check if research needed, update state
2. When you message me: I check state, spawn research if due
3. Research subagent: Does the actual work
4. Results: Written to memory, optionally announced

**Pros:**
- Best of both worlds
- Reliable hourly baseline
- Flexible when active
- Efficient resource usage

**Cons:**
- More complex to implement
- Requires state management

## Implementation Recommendations

### For Immediate Use (Architecture B - Simple Cron)

1. **Create 3 research jobs** (one per topic):
```bash
openclaw cron add --name "research-openclaw" --cron "0 * * * *" --session isolated --agent-turn "Research latest OpenClaw features" --model ollama/qwen2.5:14b --delivery none

openclaw cron add --name "research-ai" --cron "0 */3 * * *" --session isolated --agent-turn "Research AI developments" --model ollama/qwen2.5:14b --delivery none

openclaw cron add --name "research-income" --cron "0 */6 * * *" --session isolated --agent-turn "Research passive income ideas" --model ollama/qwen2.5:14b --delivery none
```

2. **Topics rotate**: OpenClaw (hourly) → AI (every 3h) → Income (every 6h)

3. **Results**: Written to `memory/research/{topic}-{date}.md`

### For Advanced Use (Architecture A - Orchestrator)

1. **Update config** for nested subagents:
```json
{
  "agents": {
    "defaults": {
      "subagents": {
        "maxSpawnDepth": 2,
        "maxChildrenPerAgent": 3,
        "runTimeoutSeconds": 0
      }
    }
  }
}
```

2. **Spawn orchestrator** from main session:
```javascript
sessions_spawn({
  agentId: "main",
  task: "You are a research orchestrator...",
  model: "ollama/qwen2.5:14b",
  runtime: "subagent",
  mode: "run",
  timeoutSeconds: 0
})
```

3. **Orchestrator spawns workers** every 30 minutes

## Resource Considerations

**RAM Usage:**
- qwen2.5:14b: ~8.5 GB when loaded
- Orchestrator: Keeps model loaded continuously
- Cron approach: Model loads/unloads per run

**API Costs:**
- Local models: Zero API cost
- Cloud models (Kimi): ~$0.01-0.10 per research task

**Storage:**
- Research files: ~10-50 KB each
- Cron logs: Pruned automatically (2MB default)
- Session retention: 24h default

## Conclusion

For your use case (24/7 background research on local model), **Architecture B (Simple Cron)** is recommended:

- Reliable and proven
- No complex orchestration
- Efficient resource usage
- Easy to monitor and debug
- Can evolve to Architecture D later

The current long-running research agent will complete its task, but for truly continuous operation, switching to scheduled cron jobs with isolated sessions is the robust solution.

## Sources
- OpenClaw Documentation: https://docs.openclaw.ai/tools/subagents
- OpenClaw Documentation: https://docs.openclaw.ai/automation/cron-jobs
- GitHub Issues: ollama/ollama #14550, #14487, #14444
- Configuration tested: 2026-03-05
