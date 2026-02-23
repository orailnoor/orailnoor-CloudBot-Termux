#!/data/data/com.termux/files/usr/bin/bash
echo "=== Your OpenClaw Gateway Token ==="
grep -o '"token":"[^"]*"' ~/.openclaw/openclaw.json | head -1
echo ""
echo "Copy the token value (without quotes) and paste it in the browser login."
