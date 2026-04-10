@echo off
echo Starting Chrome with CDP on port 9222 and CDP Proxy on port 3456...

:: Kill existing Chrome processes only (leave node.exe alone)
taskkill /F /IM chrome.exe >nul 2>&1
timeout /t 2 /nobreak >nul

:: Start Chrome with remote debugging on port 9222
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir=C:\Users\Karen\.openclaw\chrome-cdp-profile --no-first-run --no-default-browser-check

:: Wait for Chrome to initialize
timeout /t 3 /nobreak >nul

:: Start CDP Proxy. If port 3456 is already in use by another proxy, it will exit gracefully.
start "CDP-Proxy" "C:\Program Files\nodejs\node.exe" "C:\Users\Karen\.openclaw\workspace\skills\browser-cdp\cdp-proxy.mjs"

echo Chrome CDP and Proxy started.
echo - Chrome debug port: 9222
echo - CDP Proxy port: 3456
