# OpenClaw Bug Report: Node Run Process Leak

## Summary
The `nodes action=run` command spawns a new `node run` process for each execution, but these processes do not terminate after the command completes. This causes rapid accumulation of node processes, leading to system resource exhaustion.

## Environment
- **OpenClaw Version:** 2026.2.17 (4130875)
- **OS:** Windows 11 (DESKTOP-M8AO8LN)
- **Node.js:** v24.13.1
- **Gateway Port:** 18789 (changed to 18788)

## Steps to Reproduce
1. Start OpenClaw gateway
2. Execute multiple `nodes action=run` commands
3. Observe node process count growing with each command

## Expected Behavior
Each `node run` process should:
1. Spawn when command is received
2. Execute the command
3. Return result to gateway
4. **Terminate cleanly**

## Actual Behavior
Each `node run` process:
1. Spawns when command is received
2. Executes the command
3. Returns result to gateway
4. **Continues running indefinitely**

## Evidence
Process list showing multiple `node run` processes:
```
ProcessId CommandLine
--------- -----------
8752  "node.exe" ...openclaw\dist\index.js node run --host 100.75.72.26 --port 18789
7660  "node.exe" ...openclaw\dist\index.js node run --host 100.75.72.26 --port 18789
12512 "node.exe" ...openclaw\dist\index.js node run --host 100.75.72.26 --port 18789
19832 "node.exe" ...openclaw\dist\index.js node run --host 100.75.72.26 --port 18789
... (continues growing)
```

## Impact
- **Performance:** System slows as node processes accumulate
- **Stability:** Gateway restart required to clean up
- **User Experience:** Anxiety from seeing many terminal windows open
- **Resource Usage:** Each node process consumes memory/CPU

## Workaround Implemented
Created `node-cleanup.ps1` script that kills `node run` processes older than 2 minutes if count exceeds 5. Scheduled to run every 5 minutes via cron job.

## Root Cause Hypothesis
The `node run` process likely has one of these issues:
1. **Connection leak:** Not closing connection to gateway after command
2. **Event loop:** Something keeping the Node.js event loop alive
3. **Promise not resolving:** Async operation never completing
4. **Signal handling:** Not responding to termination signals

## Suggested Fix
Ensure `node run` process calls `process.exit(0)` after:
- Command execution completes
- Result is sent to gateway
- All connections are closed

## Reporter
Karen (AI Assistant) via Ken Gaffney
Date: 2026-02-23
