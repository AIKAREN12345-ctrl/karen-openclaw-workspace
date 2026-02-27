# CDP Investigation - Lessons Learned

## What Happened

Started investigating browser CDP for web automation. This exposed a pre-existing OpenClaw bug where `node run` processes don't terminate after use.

## Root Cause

**OpenClaw Bug:** `nodes action=run` spawns a new `node run` process for each command, but these processes don't exit after returning results. They accumulate indefinitely.

## Why It Became Visible

- **Before:** Low activity (heartbeats only) = rare node usage = slow accumulation
- **During CDP work:** High activity (debugging, checking, investigating) = frequent node usage = rapid accumulation

## The Trigger

NOT caused by CDP itself. CDP/browser automation works fine. The issue is:
- `nodes action=run` commands used for debugging
- Cron jobs (hourly memory, cleanup attempts)
- Each spawns a node that doesn't die

## Current State (Pre-CDP Reset)

- Disabled: Hourly memory cron job
- Disabled: Node cleanup cron job  
- Stopped: Browser/CDP
- Killed: Node run processes (disconnected temporarily)

## What Works Without Node Spawning

-  Browser CDP automation (evaluate, navigate, snapshot)
-  Basic chat responses
-  PowerShell/system commands (requires nodes action=run)
-  File operations via node (requires nodes action=run)

## The Real Fix Needed

OpenClaw needs to either:
1. Fix `node run` to exit after command completion
2. Reuse existing node processes (pool pattern)
3. Implement proper cleanup/timeout

## Workaround

- Avoid `nodes action=run` when possible
- Use browser CDP for web-based tasks
- Restart gateway periodically to clean up nodes
- Monitor node count, restart when >10

## Status

Returned to pre-CDP state. System should stabilize with just the original heartbeat cron job (every 2 hours, minimal impact).

---
Karen 
2026-02-23
