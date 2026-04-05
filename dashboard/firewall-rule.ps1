# Firewall rule for Karen Dashboard
New-NetFirewallRule -DisplayName "Karen Dashboard" -Direction Inbound -Protocol TCP -LocalPort 3000 -Action Allow