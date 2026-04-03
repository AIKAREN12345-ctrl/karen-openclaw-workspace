# POST-UPDATE-2026.2.24.md - Upgrade Log & Lessons

**Update Date:** 2026-02-25
**From Version:** 2026.2.17
**To Version:** 2026.2.24
**Status:** Completed with issues resolved

---

##  Why We Updated

**Expected fixes:**
- GitHub Issue #18198 - Ollama localhost fetch bug
- Security improvements
- General stability

**Actual result:**
-  Ollama issue NOT fixed (separate research doc)
-  Security model changed (breaking changes)
-  Node connection required reconfiguration

---

##  Breaking Changes Encountered

### 1. Control UI Security (BLOCKER)
**Error:** `non-loopback Control UI requires gateway.controlUi.allowedOrigins`

**Fix Required:**
```json
"gateway": {
  "controlUi": {
    "dangerouslyAllowHostHeaderOriginFallback": true
  }
}
```

**Applied:** Yes, in openclaw.json

### 2. Node Connection Security (BLOCKER)
**Error:** `Cannot connect to "100.75.75.72.26" over plaintext ws://`

**Root Cause:** New version requires secure connections for non-loopback

**Fix Required:**
```json
// node.json
"gateway": {
  "host": "127.0.0.1",
  "port": 18788,
  "tls": false
}
```

**Changed From:** `100.75.72.26` (Tailscale IP)
**Changed To:** `127.0.0.1` (localhost)

**Applied:** Yes, manually edited node.json

### 3. Port Conflicts
**Issue:** Old node processes holding port 18788

**Fix:**
```powershell
taskkill /F /IM node.exe
```

**Applied:** Yes, multiple times during troubleshooting

---

##  Update Procedure (For Future Reference)

### Step 1: Pre-Update
```powershell
# Stop everything
openclaw gateway stop
taskkill /F /IM node.exe

# Backup config
copy ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.backup
```

### Step 2: Update
```powershell
# Update via npm
npm i -g openclaw@latest

# Or if that fails, download and install manually
```

### Step 3: Post-Update Configuration
```powershell
# Add controlUi setting if missing
openclaw config set gateway.controlUi.dangerouslyAllowHostHeaderOriginFallback true

# Or manually edit openclaw.json
```

### Step 4: Node Reconfiguration
```powershell
# Edit node.json - change host to 127.0.0.1
notepad ~/.openclaw/node.json
```

### Step 5: Start Services
```powershell
# Start gateway
openclaw gateway start

# Start node
openclaw node run
```

### Step 6: Verify
```powershell
# Check status
openclaw status

# Check node connection
openclaw nodes status
```

---

##  Issues During Update

| Issue | Severity | Resolution | Time to Fix |
|-------|----------|------------|-------------|
| Control UI security | Critical | Config change | 15 min |
| Node connection | Critical | node.json edit | 30 min |
| Port conflicts | Medium | Kill processes | 10 min |
| npm timeout | Medium | Manual retry | 20 min |

**Total downtime:** ~75 minutes

---

##  What Worked

1. **Config backup mindset** - We didn't lose settings
2. **Manual node.json edit** - Direct fix for connection issue
3. **Process killing** - Clean slate approach worked
4. **Documentation** - This file will help next time

---

##  What Didn't Work

1. **Automatic update** - `openclaw update` failed (not git install)
2. **npm install** - Timed out, required manual retry
3. **Scheduled task stop** - Didn't kill orphaned processes
4. **Assuming fixes would work** - Ollama issue not resolved

---

##  Key Lessons

### For Next Update:
1. **Always backup configs first**
2. **Expect breaking changes in security**
3. **Kill all node processes before updating**
4. **Check node.json connection settings**
5. **Don't assume GitHub issue fixes will work**

### General Principles:
- **Test after update** - Don't assume it works
- **Document immediately** - While it's fresh
- **Have rollback plan** - Backup configs
- **Check security changes** - They're usually breaking

---

##  Security Changes in 2026.2.24

### New Requirements:
1. **Control UI origin validation** - Must specify allowed origins
2. **Node connection encryption** - ws:// only for localhost
3. **Gateway token strength** - Enforced minimum length

### Our Configuration:
- Control UI: `dangerouslyAllowHostHeaderOriginFallback: true`
- Node: `ws://127.0.0.1:18788` (localhost only)
- Token: 64 chars (already compliant)

**Assessment:** Acceptable for local/home use. Not suitable for remote access without TLS.

---

##  Related Documentation

- OLLAMA-ISSUE-SUMMARY.md - Why the update didn't fix our main issue
- TOOLS.md - Current system capabilities
- FILE-INDEX.md - Where config files live

---

##  Rollback Procedure (If Needed)

```powershell
# Stop services
openclaw gateway stop
taskkill /F /IM node.exe

# Restore config
copy ~/.openclaw/openclaw.json.backup ~/.openclaw/openclaw.json

# Reinstall old version
npm i -g openclaw@2026.2.17

# Start services
openclaw gateway start
openclaw node run
```

---

##  Final Thoughts

**The update was necessary** for security, but **disruptive** due to breaking changes.

**The Ollama issue was NOT fixed** by this update - separate architectural problem.

**Our system is now:**
-  More secure
-  Properly configured for localhost-only operation
-  Documented for future updates
-  Still has Ollama limitation (documented separately)

**Next update:** Will be smoother with this documentation.

---

*"Updates are like surgery - necessary, but document the scars."* 