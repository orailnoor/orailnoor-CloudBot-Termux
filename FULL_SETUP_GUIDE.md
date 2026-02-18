# 🎬 OpenClaw Phone AI — Complete Setup Guide (From Scratch)

> **Device:** Any Android phone (Rooted, Shizuku, or Non-Rooted)
> **Time:** ~10 minutes
> **What you need:** Termux installed from F-Droid (NOT Play Store)

### 📊 Feature Compatibility

| Feature | 🔓 Root (Magisk) | 🛡️ Shizuku | 📱 No Root |
|---------|:-:|:-:|:-:|
| Open apps | ✅ | ✅ | ✅ |
| YouTube search (deep link) | ✅ | ✅ | ✅ |
| Open URLs | ✅ | ✅ | ✅ |
| Make calls / SMS | ✅ | ✅ | ✅ |
| Battery level | ✅ | ✅ | ✅ |
| WhatsApp messages | ✅ | ✅ | ✅ |
| Play Store search | ✅ | ✅ | ✅ |
| WiFi / Bluetooth toggle | ✅ | ✅ | ❌ |
| Brightness control | ✅ | ✅ | ❌ |
| 🤖 Vision Agent (tap/swipe) | ✅ | ✅ | ❌ |
| 📸 Screenshots | ✅ | ✅ | ❌ |

> **Non-rooted users:** You get full access to app control, deep links, calls, SMS, and battery.
> For screen control (taps, swipes, screenshots), install **[Shizuku](https://shizuku.rikka.app/)** — no root needed!

---

## PHASE 1: Install Termux

1. Download **Termux** from **F-Droid**: https://f-droid.org/en/packages/com.termux/
2. Open Termux

---

## PHASE 2: Base Setup (Run in Termux)

### Step 1 — Update packages
```bash
yes | pkg update && yes | pkg upgrade
```

### Step 2 — Install dependencies
```bash
pkg install -y nodejs-lts git curl
```

### Step 3 — Fix network interface error (required for OpenClaw)
```bash
cat > /data/data/com.termux/files/usr/bin/ifconfig << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
echo "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536"
echo "        inet 127.0.0.1  netmask 255.0.0.0"
echo "        loop  txqueuelen 1000  (Local Loopback)"
EOF
chmod +x /data/data/com.termux/files/usr/bin/ifconfig
```

---

## PHASE 3: Install OpenClaw

### Step 4 — Install OpenClaw CLI
```bash
npm install -g openclaw@latest --ignore-scripts
cd /data/data/com.termux/files/usr/lib/node_modules/openclaw && npm rebuild koffi
```

### Step 5 — Onboard (creates config + workspace)
```bash
openclaw onboard
```
> It will ask for a **Telegram Bot Token** and **Chat ID**.
> If you don't have these yet, you can skip and configure later.

### Step 6 — Set your Gemini API key
```bash
openclaw auth add google --key "YOUR_GEMINI_API_KEY_HERE"
```

---

## PHASE 4: Deploy Phone Control Scripts

### Step 7 — Create phone_control.sh
```bash
cat > ~/phone_control.sh << 'SCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
CMD="$1"
shift

# Smart privilege detection: su (root) → rish (Shizuku) → direct
if su -c 'echo ok' 2>/dev/null | grep -q ok; then
  PRIV="root"
elif command -v rish &>/dev/null && rish -c 'echo ok' 2>/dev/null | grep -q ok; then
  PRIV="shizuku"
else
  PRIV="none"
fi

run_cmd() {
  case "$PRIV" in
    root)    su -c "$@" ;;
    shizuku) rish -c "$@" ;;
    none)    eval "$@" 2>/dev/null ;;
  esac
}

case "$CMD" in
  screenshot)
    FILENAME="${1:-/sdcard/screenshot_$(date +%s).png}"
    run_cmd "screencap '$FILENAME'"
    echo "📸 Screenshot saved: $FILENAME"
    ;;
  tap)
    run_cmd "input tap $1 $2"
    echo "👆 Tapped at ($1, $2)"
    ;;
  swipe)
    run_cmd "input swipe $1 $2 $3 $4 ${5:-300}"
    echo "👆 Swiped from ($1,$2) to ($3,$4)"
    ;;
  type)
    run_cmd "input text '$*'"
    echo "⌨️ Typed: $*"
    ;;
  key)
    run_cmd "input keyevent $1"
    echo "🔘 Key pressed: $1"
    ;;
  open-app)
    run_cmd "monkey -p $1 -c android.intent.category.LAUNCHER 1" 2>/dev/null
    echo "📱 Opened: $1"
    ;;
  kill-app)
    run_cmd "am force-stop $1"
    echo "❌ Killed: $1"
    ;;
  youtube-search)
    QUERY=$(echo "$*" | sed 's/ /+/g')
    run_cmd "am start -a android.intent.action.VIEW -d 'https://www.youtube.com/results?search_query=$QUERY' com.google.android.youtube"
    echo "🔍 YouTube search: $*"
    ;;
  open-url)
    run_cmd "am start -a android.intent.action.VIEW -d '$1'"
    echo "🌐 Opened: $1"
    ;;
  whatsapp-send)
    NUM="$1"; shift; MSG=$(echo "$*" | sed 's/ /%20/g')
    run_cmd "am start -a android.intent.action.VIEW -d 'https://wa.me/$NUM?text=$MSG'"
    echo "📱 WhatsApp to $NUM"
    ;;
  playstore-search)
    QUERY=$(echo "$*" | sed 's/ /+/g')
    run_cmd "am start -a android.intent.action.VIEW -d 'market://search?q=$QUERY'"
    echo "🔍 Play Store search: $*"
    ;;
  install-app)
    run_cmd "am start -a android.intent.action.VIEW -d 'market://details?id=$1'"
    echo "📦 Opened Play Store for: $1"
    ;;
  wifi)
    case "$1" in
      on)  run_cmd "svc wifi enable"  && echo "📶 WiFi ON" ;;
      off) run_cmd "svc wifi disable" && echo "📶 WiFi OFF" ;;
    esac
    ;;
  bluetooth)
    case "$1" in
      on)  run_cmd "svc bluetooth enable"  && echo "🔵 Bluetooth ON" ;;
      off) run_cmd "svc bluetooth disable" && echo "🔵 Bluetooth OFF" ;;
    esac
    ;;
  airplane)
    case "$1" in
      on)  run_cmd "cmd connectivity airplane-mode enable" && echo "✈️ Airplane ON" ;;
      off) run_cmd "cmd connectivity airplane-mode disable" && echo "✈️ Airplane OFF" ;;
    esac
    ;;
  brightness)
    run_cmd "settings put system screen_brightness $1"
    echo "🔆 Brightness: $1/255"
    ;;
  send-sms)
    NUM="$1"; shift; MSG="$*"
    run_cmd "am start -a android.intent.action.SENDTO -d sms:$NUM --es sms_body '$MSG'"
    echo "📩 SMS to $NUM"
    ;;
  call)
    run_cmd "am start -a android.intent.action.CALL -d tel:$1"
    echo "📞 Calling: $1"
    ;;
  battery)
    run_cmd "dumpsys battery" | grep "level"
    ;;
  home)
    run_cmd "input keyevent 3"
    echo "🏠 Home"
    ;;
  back)
    run_cmd "input keyevent 4"
    echo "◀️ Back"
    ;;
  *)
    echo "Usage: bash phone_control.sh [command] [args]"
    echo "Commands: screenshot, tap, swipe, type, key, open-app, kill-app,"
    echo "  youtube-search, open-url, whatsapp-send, playstore-search,"
    echo "  wifi, bluetooth, airplane, brightness, battery, call, send-sms"
    ;;
esac
SCRIPT
chmod +x ~/phone_control.sh
echo "✅ phone_control.sh created"
```

### Step 8 — Create phone_agent.sh (Vision AI Agent)
```bash
cat > ~/phone_agent.sh << 'AGENTSCRIPT'
#!/data/data/com.termux/files/usr/bin/bash
MODEL="gemini-2.5-flash-lite"
MAX_STEPS=15
SCREENSHOT_PATH="/sdcard/agent_screen.png"
PAYLOAD_FILE="/sdcard/agent_payload.json"
RESPONSE_FILE="/sdcard/agent_response.json"

# Smart privilege detection: su (root) → rish (Shizuku) → direct
if su -c 'echo ok' 2>/dev/null | grep -q ok; then
  PRIV="root"; PRIV_CMD="su -c"
elif command -v rish &>/dev/null && rish -c 'echo ok' 2>/dev/null | grep -q ok; then
  PRIV="shizuku"; PRIV_CMD="rish -c"
else
  PRIV="none"; PRIV_CMD=""
  echo "⚠️ No root/Shizuku. Vision agent requires screen control privileges."
  echo "   Install Shizuku or use a rooted device for full functionality."
  exit 1
fi

rcmd() {
  case "$PRIV" in
    root)    su -c "$@" ;;
    shizuku) rish -c "$@" ;;
  esac
}

# Auto-detect screen size
SCREEN_SIZE=$(rcmd "wm size" 2>/dev/null | grep -o '[0-9]*x[0-9]*' | tail -1)
SCREEN_W=$(echo "$SCREEN_SIZE" | cut -dx -f1)
SCREEN_H=$(echo "$SCREEN_SIZE" | cut -dx -f2)
[ -z "$SCREEN_W" ] && SCREEN_W=1080
[ -z "$SCREEN_H" ] && SCREEN_H=2400
CENTER_X=$((SCREEN_W / 2))
echo "📱 Screen: ${SCREEN_W}x${SCREEN_H} (via $PRIV)"

load_api_key() {
    local AUTH_FILE="$HOME/.openclaw/agents/main/agent/auth-profiles.json"
    if [ -f "$AUTH_FILE" ]; then
        grep -o '"key"[[:space:]]*:[[:space:]]*"[^"]*"' "$AUTH_FILE" | head -1 | sed 's/.*"key"[[:space:]]*:[[:space:]]*"//;s/"$//'
    else
        echo "$GEMINI_API_KEY"
    fi
}

do_action() {
    local ATYPE="$1"
    case "$ATYPE" in
        tap) rcmd "input tap $2 $3" 2>/dev/null; echo "  👆 Tap ($2, $3)" ;;
        swipe) rcmd "input swipe $2 $3 $4 $5 ${6:-300}" 2>/dev/null; echo "  👆 Swipe ($2,$3)→($4,$5)" ;;
        type) local ESCAPED=$(echo "$2" | sed 's/ /%s/g'); rcmd "input text '$ESCAPED'" 2>/dev/null; echo "  ⌨️ Type: $2" ;;
        key) rcmd "input keyevent $2" 2>/dev/null; echo "  🔘 Key: $2" ;;
        open_app) rcmd "monkey -p $2 -c android.intent.category.LAUNCHER 1" 2>/dev/null; echo "  📱 Open: $2"; sleep 2 ;;
        scroll_down) rcmd "input swipe $CENTER_X $((SCREEN_H*7/10)) $CENTER_X $((SCREEN_H*3/10)) 300" 2>/dev/null; echo "  ⬇️ Scroll down" ;;
        scroll_up) rcmd "input swipe $CENTER_X $((SCREEN_H*3/10)) $CENTER_X $((SCREEN_H*7/10)) 300" 2>/dev/null; echo "  ⬆️ Scroll up" ;;
        go_home) rcmd "input keyevent 3" 2>/dev/null; echo "  🏠 Home" ;;
        go_back) rcmd "input keyevent 4" 2>/dev/null; echo "  ◀️ Back" ;;
        wait) echo "  ⏳ Wait ${2:-1}s"; sleep "${2:-1}" ;;
        done) echo "  ✅ $2" ;;
    esac
}

if [ -z "$1" ]; then
    echo "🤖 Phone Agent"; echo 'Usage: bash phone_agent.sh "<task>"'; exit 0
fi

TASK="$*"
API_KEY=$(load_api_key)
[ -z "$API_KEY" ] && echo "❌ No API key!" && exit 1

echo ""; echo "🤖 PHONE AGENT v2"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 Task: $TASK"; echo "🧠 Model: $MODEL"; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

HISTORY=""
URL="https://generativelanguage.googleapis.com/v1beta/models/${MODEL}:generateContent?key=${API_KEY}"
SYSTEM="You are an Android phone agent (${SCREEN_W}x${SCREEN_H}). You see a screenshot and a list of UI elements with exact coordinates. Use the UI element coordinates for precision.\n\nACTIONS (JSON only):\n{\"thought\": \"what I see and plan\", \"actions\": [{\"action\": \"tap\", \"x\": ${CENTER_X}, \"y\": 500}]}\n\nAction types: tap(x,y), swipe(x1,y1,x2,y2), type(text), key(code: 3=HOME 4=BACK 66=ENTER), open_app(package), scroll_down, scroll_up, go_home, go_back, wait(seconds), done(message).\n\nPackages: com.whatsapp, com.google.android.youtube, com.instagram.android, com.android.chrome, com.android.settings\n\nIMPORTANT RULES:\n1. JSON only, 1-2 actions per step.\n2. PREFER using UI element coordinates over guessing.\n3. If a tap did not work, try DIFFERENT coordinates or a different approach.\n4. When you need to type, first make sure a text input field is focused (keyboard visible).\n5. Use open_app to launch apps, then wait 2-3s.\n6. Use done when the task is complete."

for STEP in $(seq 1 $MAX_STEPS); do
    echo ""; echo "── STEP $STEP/$MAX_STEPS ──"
    echo "  📸 Capturing..."
    rcmd "screencap -p $SCREENSHOT_PATH" 2>/dev/null
    sleep 0.5
    [ ! -s "$SCREENSHOT_PATH" ] && echo "  ❌ Screenshot failed" && sleep 1 && continue

    echo "  🔍 Reading UI..."
    rcmd "uiautomator dump /sdcard/ui.xml" 2>/dev/null
    sleep 0.3
    UI_ELEMENTS=$(rcmd "cat /sdcard/ui.xml" 2>/dev/null | grep -o 'text="[^"]*"[^>]*bounds="\[[0-9]*,[0-9]*\]\[[0-9]*,[0-9]*\]"' | head -20 | while read -r line; do
        txt=$(echo "$line" | sed -n 's/.*text="\([^"]*\)".*/\1/p')
        bnds=$(echo "$line" | sed -n 's/.*bounds="\([^"]*\)".*/\1/p')
        x1=$(echo "$bnds" | sed 's/\[//g;s/\]/ /g' | awk '{print $1}' | cut -d, -f1)
        y1=$(echo "$bnds" | sed 's/\[//g;s/\]/ /g' | awk '{print $1}' | cut -d, -f2)
        x2=$(echo "$bnds" | sed 's/\[//g;s/\]/ /g' | awk '{print $2}' | cut -d, -f1)
        y2=$(echo "$bnds" | sed 's/\[//g;s/\]/ /g' | awk '{print $2}' | cut -d, -f2)
        if [ -n "$x1" ] && [ -n "$y1" ] && [ -n "$x2" ] && [ -n "$y2" ]; then
            cx=$(( (x1 + x2) / 2 )); cy=$(( (y1 + y2) / 2 ))
            [ -n "$txt" ] && echo "$txt center($cx,$cy)"
        fi
    done 2>/dev/null)
    UI_COUNT=$(echo "$UI_ELEMENTS" | grep -c "center" 2>/dev/null)
    echo "  📋 $UI_COUNT elements"

    ESCAPED_TASK=$(echo "$TASK" | sed 's/"/\\"/g')
    ESCAPED_UI=$(echo "$UI_ELEMENTS" | tr '\n' ' ' | sed 's/"/\\"/g')
    USER_MSG="TASK: ${ESCAPED_TASK}. Step ${STEP}/${MAX_STEPS}. ${HISTORY}UI Elements: ${ESCAPED_UI}. Analyze screenshot and UI elements, respond JSON only."

    rm -f "$PAYLOAD_FILE" 2>/dev/null
    printf '{"systemInstruction":{"parts":[{"text":"%s"}]},"contents":[{"parts":[{"inline_data":{"mimeType":"image/png","data":"' "$SYSTEM" > "$PAYLOAD_FILE"
    base64 "$SCREENSHOT_PATH" | tr -d '\n' >> "$PAYLOAD_FILE"
    printf '"}},{"text":"%s"}]}],"generationConfig":{"temperature":0.2,"maxOutputTokens":512,"responseMimeType":"application/json"}}' "$USER_MSG" >> "$PAYLOAD_FILE"

    PAYLOAD_SIZE=$(wc -c < "$PAYLOAD_FILE")
    echo "  📦 Payload: ${PAYLOAD_SIZE} bytes"
    echo "  🧠 Asking Gemini..."

    HTTP_CODE=$(curl -s -w "%{http_code}" -o "$RESPONSE_FILE" -X POST "$URL" -H "Content-Type: application/json" -d "@${PAYLOAD_FILE}" --connect-timeout 15 --max-time 45 2>/dev/null)

    if [ "$HTTP_CODE" != "200" ]; then
        echo "  ❌ API error: HTTP $HTTP_CODE"
        [ -f "$RESPONSE_FILE" ] && ERROR_MSG=$(grep -oP '"message"\s*:\s*"\K[^"]*' "$RESPONSE_FILE" | head -1) && echo "  ❌ $ERROR_MSG"
        [ "$HTTP_CODE" = "429" ] && echo "  ⏳ Rate limited, waiting 10s..." && sleep 10
        continue
    fi

    RESPONSE_TEXT=$(sed -n 's/.*"text"[[:space:]]*:[[:space:]]*"\(.*\)"/\1/p' "$RESPONSE_FILE" | head -1)
    [ -z "$RESPONSE_TEXT" ] && echo "  ⚠️ Empty response" && continue
    CLEAN=$(echo "$RESPONSE_TEXT" | sed 's/\\"/"/g; s/\\n/ /g; s/\\t/ /g')
    THOUGHT=$(echo "$CLEAN" | sed -n 's/.*"thought"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    [ -z "$THOUGHT" ] && THOUGHT="thinking..."
    echo "  💭 $THOUGHT"

    ACTED=false
    if echo "$CLEAN" | grep -q '"done"'; then
        DONE_MSG=$(echo "$CLEAN" | sed -n 's/.*"message"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        echo ""; echo "  ✅ DONE: $DONE_MSG"; break
    fi
    APP_PKG=$(echo "$CLEAN" | sed -n 's/.*"open_app".*"package"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    [ -n "$APP_PKG" ] && do_action "open_app" "$APP_PKG" && ACTED=true
    if echo "$CLEAN" | grep -q '"tap"'; then
        X=$(echo "$CLEAN" | sed -n 's/.*"tap".*"x"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        Y=$(echo "$CLEAN" | sed -n 's/.*"tap".*"y"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        [ -n "$X" ] && [ -n "$Y" ] && do_action "tap" "$X" "$Y" && ACTED=true
    fi
    if echo "$CLEAN" | grep -q '"type"'; then
        TYPE_TEXT=$(echo "$CLEAN" | sed -n 's/.*"type".*"text"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
        [ -n "$TYPE_TEXT" ] && do_action "type" "$TYPE_TEXT" && ACTED=true
    fi
    if echo "$CLEAN" | grep -q '"key"'; then
        KEY_CODE=$(echo "$CLEAN" | sed -n 's/.*"key".*"code"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        [ -n "$KEY_CODE" ] && do_action "key" "$KEY_CODE" && ACTED=true
    fi
    echo "$CLEAN" | grep -q '"scroll_down"' && do_action "scroll_down" && ACTED=true
    echo "$CLEAN" | grep -q '"scroll_up"' && do_action "scroll_up" && ACTED=true
    echo "$CLEAN" | grep -q '"go_back"' && do_action "go_back" && ACTED=true
    echo "$CLEAN" | grep -q '"go_home"' && do_action "go_home" && ACTED=true
    if echo "$CLEAN" | grep -q '"wait"'; then
        WAIT_SECS=$(echo "$CLEAN" | sed -n 's/.*"wait".*"seconds"[[:space:]]*:[[:space:]]*\([0-9.]*\).*/\1/p')
        [ -n "$WAIT_SECS" ] && do_action "wait" "$WAIT_SECS" && ACTED=true
    fi
    if echo "$CLEAN" | grep -q '"swipe"'; then
        SX1=$(echo "$CLEAN" | sed -n 's/.*"swipe".*"x1"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        SY1=$(echo "$CLEAN" | sed -n 's/.*"swipe".*"y1"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        SX2=$(echo "$CLEAN" | sed -n 's/.*"swipe".*"x2"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        SY2=$(echo "$CLEAN" | sed -n 's/.*"swipe".*"y2"[[:space:]]*:[[:space:]]*\([0-9]*\).*/\1/p')
        [ -n "$SX1" ] && do_action "swipe" "$SX1" "$SY1" "$SX2" "$SY2" && ACTED=true
    fi
    [ "$ACTED" = "false" ] && echo "  ⚠️ No actions parsed"
    HISTORY="Previous: ${THOUGHT}. "
    sleep 1
done
rm -f "$PAYLOAD_FILE" "$PAYLOAD_FILE.head" "$PAYLOAD_FILE.tmp" "$RESPONSE_FILE" 2>/dev/null
echo ""; echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"; echo "🏁 Agent finished ($STEP steps)"
AGENTSCRIPT
chmod +x ~/phone_agent.sh
echo "✅ phone_agent.sh created"
```

### Step 9 — Create AGENTS.md (AI Instructions)
```bash
mkdir -p ~/.openclaw/workspace
cat > ~/.openclaw/workspace/AGENTS.md << 'AGENTSMD'
You are an autonomous AI assistant running on an Android phone via Termux.
You control the phone using shell scripts. NO Python is needed.

# ⚠️ CRITICAL RULES
- Use ONLY bash scripts listed below.
- **DO NOT** use `am start` directly.
- **DO NOT** use `python3` — it is NOT installed.
- **DO NOT** use `which` command.
- **PREFER deep-link commands** over the visual agent.

# 📱 PHONE CONTROL

## ⚡ 1. SMART COMMANDS — Instant

### App Launches
```bash
bash ~/phone_control.sh open-app com.google.android.youtube
bash ~/phone_control.sh open-app com.whatsapp
bash ~/phone_control.sh open-app com.instagram.android
bash ~/phone_control.sh open-app com.android.chrome
bash ~/phone_control.sh open-app com.android.settings
```

### Deep Links (PREFERRED)
```bash
bash ~/phone_control.sh youtube-search "lofi music"
bash ~/phone_control.sh open-url "https://google.com"
bash ~/phone_control.sh whatsapp-send 919876543210 "Hello from AI"
bash ~/phone_control.sh playstore-search "Spotify"
```

### System Controls
```bash
bash ~/phone_control.sh wifi on|off
bash ~/phone_control.sh bluetooth on|off
bash ~/phone_control.sh brightness 255
bash ~/phone_control.sh battery
bash ~/phone_control.sh call 9876543210
bash ~/phone_control.sh send-sms 9876543210 "Hello"
```

## 🤖 2. VISUAL AGENT — For Complex UI Tasks Only
```bash
bash ~/phone_agent.sh "Your task description here"
```

## 🧠 DECISION TABLE
| Request | Command |
|---------|---------|
| "Search YouTube for X" | `bash ~/phone_control.sh youtube-search "X"` |
| "Open YouTube" | `bash ~/phone_control.sh open-app com.google.android.youtube` |
| "Open google.com" | `bash ~/phone_control.sh open-url "https://google.com"` |
| "Turn on WiFi" | `bash ~/phone_control.sh wifi on` |
| "Battery level?" | `bash ~/phone_control.sh battery` |
| "Enable Dark Mode" | `bash ~/phone_agent.sh "Open Settings and enable Dark Mode"` |
AGENTSMD
echo "✅ AGENTS.md created"
```

---

## PHASE 5: Start OpenClaw

### Step 10 — Start the gateway
```bash
openclaw gateway --verbose
```

> This will print a URL like `http://127.0.0.1:18789`
> It will also show a login token. Save this!

---

## PHASE 6: Test!

### Test via Telegram (send these messages to your bot):

```
Search YouTube for lofi music
```
```
What is my battery level?
```
```
Turn on WiFi
```
```
Open google.com
```

---

## 🔧 OPTIONAL: Hide Magisk Root Toast
Open **Magisk App** → **Settings** → **Superuser Notification** → Set to **None**

---

## 📋 Quick Reference — All Commands

| Command | What it does |
|---------|-------------|
| `bash ~/phone_control.sh open-app <pkg>` | Open any app |
| `bash ~/phone_control.sh youtube-search "<query>"` | Search YouTube |
| `bash ~/phone_control.sh open-url "<url>"` | Open URL in browser |
| `bash ~/phone_control.sh whatsapp-send <num> "<msg>"` | WhatsApp message |
| `bash ~/phone_control.sh playstore-search "<app>"` | Search Play Store |
| `bash ~/phone_control.sh wifi on/off` | Toggle WiFi |
| `bash ~/phone_control.sh bluetooth on/off` | Toggle Bluetooth |
| `bash ~/phone_control.sh brightness <0-255>` | Set brightness |
| `bash ~/phone_control.sh battery` | Check battery |
| `bash ~/phone_control.sh call <number>` | Make a call |
| `bash ~/phone_control.sh send-sms <num> "<msg>"` | Send SMS |
| `bash ~/phone_control.sh screenshot` | Take screenshot |
| `bash ~/phone_agent.sh "<task>"` | AI Vision agent |
