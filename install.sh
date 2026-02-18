#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# 🤖 CloudBot-Termux — One-Command Installer
# Run: curl -sL https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main/install.sh | bash
# ============================================

set -e

echo ""
echo "🤖 CloudBot-Termux Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1: Update packages
echo "📦 Step 1/6: Updating packages..."
yes | pkg update -y 2>/dev/null
yes | pkg upgrade -y 2>/dev/null
echo "✅ Packages updated"

# Step 2: Install dependencies
echo ""
echo "📦 Step 2/6: Installing Node.js, Git, Curl..."
pkg install -y nodejs-lts git curl 2>/dev/null
echo "✅ Dependencies installed"

# Step 3: Fix ifconfig
echo ""
echo "🔧 Step 3/6: Fixing network interface..."
cat > /data/data/com.termux/files/usr/bin/ifconfig << 'IFEOF'
#!/data/data/com.termux/files/usr/bin/sh
echo "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536"
echo "        inet 127.0.0.1  netmask 255.0.0.0"
echo "        loop  txqueuelen 1000  (Local Loopback)"
IFEOF
chmod +x /data/data/com.termux/files/usr/bin/ifconfig
echo "✅ Network fix applied"

# Step 4: Install OpenClaw
echo ""
echo "📦 Step 4/6: Installing OpenClaw..."
npm install -g openclaw@latest 2>&1 || true
echo "✅ OpenClaw installed"

# Step 5: Download scripts
echo ""
echo "📥 Step 5/6: Downloading control scripts..."
REPO="https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main"
curl -sL "$REPO/phone_control.sh" > ~/phone_control.sh && chmod +x ~/phone_control.sh
curl -sL "$REPO/phone_agent.sh" > ~/phone_agent.sh && chmod +x ~/phone_agent.sh
mkdir -p ~/.openclaw/workspace
curl -sL "$REPO/AGENTS.md" > ~/.openclaw/workspace/AGENTS.md
echo "✅ Scripts downloaded"

# Step 6: Interactive setup
echo ""
echo "🔑 Step 6/6: Configuration"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Gemini API Key
echo "📌 Get your FREE Gemini API key from:"
echo "   https://aistudio.google.com/apikey"
echo ""
printf "Enter your Gemini API Key: "
read GEMINI_KEY < /dev/tty 2>/dev/null || GEMINI_KEY=""
if [ -n "$GEMINI_KEY" ]; then
    openclaw auth add google --key "$GEMINI_KEY" 2>/dev/null || true
    echo "✅ API key saved"
fi
if [ -z "$GEMINI_KEY" ]; then
    echo "⚠️  Skipped. Add later: openclaw auth add google --key YOUR_KEY"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 INSTALLATION COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Now run these two commands:"
echo ""
echo "  1. openclaw onboard     (setup Telegram bot)"
echo "  2. openclaw gateway --verbose  (start the bot)"
echo ""
echo "Then send a message to your Telegram bot!"
echo ""
echo "Example messages to try:"
echo "  • What is my battery level?"
echo "  • Search YouTube for lofi music"
echo "  • Turn on WiFi"
echo "  • Open google.com"
echo ""
echo "⭐ Star us on GitHub: github.com/orailnoor/orailnoor-CloudBot-Termux"
echo ""
