# 🤖 CloudBot-Termux

**Turn your Android phone into an AI-powered assistant — controlled entirely through Telegram.**

> Your phone opens apps, searches YouTube, sends messages, toggles WiFi, and more — all by itself. No computer needed.

---

## 📺 Demo

Send a Telegram message → AI executes it on your phone:

| You say... | Phone does... |
|---|---|
| "Search YouTube for lofi music" | Opens YouTube with search results |
| "Turn on WiFi" | WiFi toggles on |
| "What's my battery level?" | Reports exact battery % |
| "Open google.com" | Chrome opens with Google |
| "Call 1234567890" | Starts dialing |

---

## 📊 Works on ALL Phones

| Feature | 🔓 Rooted | 🛡️ Shizuku | 📱 No Root |
|---------|:-:|:-:|:-:|
| Open apps | ✅ | ✅ | ✅ |
| YouTube search | ✅ | ✅ | ✅ |
| Open URLs | ✅ | ✅ | ✅ |
| Calls / SMS | ✅ | ✅ | ✅ |
| Battery check | ✅ | ✅ | ✅ |
| WhatsApp messages | ✅ | ✅ | ✅ |
| WiFi / Bluetooth | ✅ | ✅ | ❌ |
| 🤖 Vision Agent | ✅ | ✅ | ❌ |

---

## ⚡ Quick Install (One Command)

Open **Termux** (install from [F-Droid](https://f-droid.org/en/packages/com.termux/), NOT Play Store) and run:

```bash
curl -sL https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main/install.sh | bash
```

Then follow the on-screen prompts to enter your:
1. **Telegram Bot Token** (from [@BotFather](https://t.me/BotFather))
2. **Telegram Chat ID** (from [@userinfobot](https://t.me/userinfobot))
3. **Gemini API Key** (free from [Google AI Studio](https://aistudio.google.com/apikey))

---

## 📖 Manual Setup

If you prefer step-by-step, see **[FULL_SETUP_GUIDE.md](FULL_SETUP_GUIDE.md)**.

### Prerequisites
- Android phone (Android 10+)
- [Termux](https://f-droid.org/en/packages/com.termux/) from F-Droid
- [Telegram Bot Token](https://t.me/BotFather)
- [Gemini API Key](https://aistudio.google.com/apikey) (free tier available)

### Steps

**1. Update & install base packages:**
```bash
yes | pkg update && yes | pkg upgrade
pkg install -y nodejs git curl cmake
```

**2. Fix network interface (required):**
```bash
cat > /data/data/com.termux/files/usr/bin/ifconfig << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
echo "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536"
echo "        inet 127.0.0.1  netmask 255.0.0.0"
echo "        loop  txqueuelen 1000  (Local Loopback)"
EOF
chmod +x /data/data/com.termux/files/usr/bin/ifconfig
```

**3. Install OpenClaw:**
```bash
npm install -g openclaw@2026.2.19 --ignore-scripts
openclaw onboard
```

**4. Set your Gemini API key:**
```bash
openclaw auth add google --key "YOUR_GEMINI_API_KEY"
```

**5. Download scripts:**
```bash
curl -sL https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main/phone_control.sh > ~/phone_control.sh && chmod +x ~/phone_control.sh
curl -sL https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main/phone_agent.sh > ~/phone_agent.sh && chmod +x ~/phone_agent.sh
curl -sL https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main/AGENTS.md > ~/.openclaw/workspace/AGENTS.md
```

**6. Start the bot:**
```bash
openclaw gateway --verbose
```

Done! Send a message to your Telegram bot 🎉

---

## 🧠 How It Works

```
You (Telegram) → OpenClaw Gateway → AI Model (Gemini) → Shell Commands → Your Phone
```

1. You send a message via Telegram
2. OpenClaw receives it and sends to Gemini AI
3. Gemini decides which command to run
4. The command executes on your phone
5. Result is sent back to Telegram

### Vision Agent (Advanced)
For complex tasks like navigating app UIs, the **Vision Agent** (`phone_agent.sh`):
- Takes a screenshot of your phone
- Sends it to Gemini Vision API
- AI decides where to tap/swipe/type
- Repeats until task is complete

---

## 📋 Available Commands

| Command | What it does |
|---------|-------------|
| `bash ~/phone_control.sh open-app <pkg>` | Open any app |
| `bash ~/phone_control.sh youtube-search "<query>"` | Search YouTube directly |
| `bash ~/phone_control.sh open-url "<url>"` | Open any URL |
| `bash ~/phone_control.sh whatsapp-send <num> "<msg>"` | Send WhatsApp message |
| `bash ~/phone_control.sh playstore-search "<app>"` | Search Play Store |
| `bash ~/phone_control.sh wifi on/off` | Toggle WiFi |
| `bash ~/phone_control.sh bluetooth on/off` | Toggle Bluetooth |
| `bash ~/phone_control.sh brightness <0-255>` | Set brightness |
| `bash ~/phone_control.sh battery` | Check battery level |
| `bash ~/phone_control.sh call <number>` | Make a phone call |
| `bash ~/phone_control.sh send-sms <num> "<msg>"` | Send SMS |
| `bash ~/phone_control.sh screenshot` | Take screenshot |
| `bash ~/phone_agent.sh "<task>"` | AI Vision agent |

---

## 💰 Cost

Uses **Gemini 2.5 Flash Lite** — Google's cheapest AI model:

| Usage | Monthly Cost |
|---|---|
| Light (10 tasks/day) | ~$0.24 |
| Medium (50 tasks/day) | ~$1.20 |
| Heavy (200 tasks/day) | ~$4.80 |

**Free tier:** 1,500 requests/day at no cost!

---

## 🔧 Troubleshooting

| Issue | Fix |
|---|---|
| "Gateway service not supported" | Normal on Android — run `openclaw gateway --verbose` manually |
| Magisk root toast notifications | Magisk → Settings → Superuser Notification → None |
| Screen flipped | `adb shell settings put system user_rotation 0` |

---

## 📄 License

MIT License — use freely!

---

## ⭐ Star this repo if it helped you!

Made with ❤️ by [@orailnoor](https://github.com/orailnoor)
