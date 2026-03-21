# Restart OpenClaw Node with Screen Capability Enabled
# Run this to enable VNC screen recording via nodes command

$env:OPENCLAW_NODE_SCREEN_ENABLED = "true"
$env:OPENCLAW_NODE_VNC_HOST = "localhost"
$env:OPENCLAW_NODE_VNC_PORT = "5900"
$env:OPENCLAW_NODE_VNC_PASSWORD = $env:VNC_PASS

Write-Host "Environment variables set for VNC screen recording"
Write-Host "VNC Host: localhost:5900"
Write-Host "Starting OpenClaw..."

# Start OpenClaw (adjust path if needed)
openclaw
