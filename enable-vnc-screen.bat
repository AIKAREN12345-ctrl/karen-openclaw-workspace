@echo off
echo Creating OpenClaw Node task with VNC screen support...

schtasks /Delete /TN "OpenClaw Node" /F 2>nul

schtasks /Create /TN "OpenClaw Node" /TR "powershell -WindowStyle Hidden -Command \"$env:OPENCLAW_NODE_SCREEN_ENABLED='true'; $env:OPENCLAW_NODE_VNC_HOST='localhost'; $env:OPENCLAW_NODE_VNC_PORT='5900'; $env:OPENCLAW_NODE_VNC_PASSWORD='%VNC_PASS%'; node 'C:\Users\Karen\AppData\Roaming\npm\node_modules\openclaw\dist\index.js' node\"" /SC ONLOGON /RL HIGHEST /F

echo Task created. Starting...
schtasks /Run /TN "OpenClaw Node"
