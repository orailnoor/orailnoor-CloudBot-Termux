#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# OpenClaw API Key Switcher
# Usage: bash switch_api.sh [1|2|3|show]
# ============================================

KEY_1="YOUR_API_KEY_1"
KEY_2="YOUR_API_KEY_2"
KEY_3="YOUR_API_KEY_3"

AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
CONFIG_FILE="$HOME/.openclaw/openclaw.json"

update_key() {
  NEW_KEY="$1"
  # Update auth profile
  sed -i "s/\"key\": \"[^\"]*\"/\"key\": \"$NEW_KEY\"/" "$AUTH_FILE"
  # Update openclaw generic config (skills, etc if present)
  sed -i "s/\"apiKey\": \"[^\"]*\"/\"apiKey\": \"$NEW_KEY\"/" "$CONFIG_FILE"
}

case "$1" in
  1)
    echo "🔑 Switching to API Key 1..."
    update_key "$KEY_1"
    echo "✅ Now using Key 1: ${KEY_1:0:10}...${KEY_1: -4}"
    echo "⚠️  Restart gateway: openclaw gateway --verbose"
    ;;
  2)
    echo "🔑 Switching to API Key 2..."
    update_key "$KEY_2"
    echo "✅ Now using Key 2: ${KEY_2:0:10}...${KEY_2: -4}"
    echo "⚠️  Restart gateway: openclaw gateway --verbose"
    ;;
  3)
    echo "🔑 Switching to API Key 3..."
    update_key "$KEY_3"
    echo "✅ Now using Key 3: ${KEY_3:0:10}...${KEY_3: -4}"
    echo "⚠️  Restart gateway: openclaw gateway --verbose"
    ;;
  show)
    CURRENT=$(grep -o '"key": "[^"]*"' "$AUTH_FILE" | head -1 | cut -d'"' -f4)
    echo "📋 Available API Keys:"
    echo ""
    for k in "$KEY_1" "$KEY_2" "$KEY_3"; do
      if [ "$CURRENT" = "$k" ]; then
        echo "  [*] ${k:0:10}...${k: -4}  ← ACTIVE ✅"
      else
        echo "  [ ] ${k:0:10}...${k: -4}"
      fi
    done
    ;;
  *)
    echo "Usage: bash switch_api.sh [1|2|3|show]"
    echo ""
    echo "  1/2/3 - Switch to specific API Key"
    echo "  show  - Show which key is active"
    echo ""
    echo "After switching, restart the gateway:"
    echo "  Ctrl+C (stop gateway)"
    echo "  openclaw gateway --verbose"
    ;;
esac
