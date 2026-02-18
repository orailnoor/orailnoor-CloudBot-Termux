#!/data/data/com.termux/files/usr/bin/bash
# CloudBot-Termux Installer

echo ""
echo "🤖 CloudBot-Termux Installer"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Step 1
echo "📦 Step 1/6: Updating packages..."
yes | pkg update
yes | pkg upgrade
echo "✅ Done"

# Step 2
echo ""
echo "📦 Step 2/6: Installing dependencies..."
pkg install -y nodejs-lts git curl cmake
echo "✅ Done"

# Step 3
echo ""
echo "🔧 Step 3/6: Fixing network interface..."
cat > /data/data/com.termux/files/usr/bin/ifconfig << 'EOF'
#!/data/data/com.termux/files/usr/bin/sh
echo "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536"
echo "        inet 127.0.0.1  netmask 255.0.0.0"
echo "        loop  txqueuelen 1000  (Local Loopback)"
EOF
chmod +x /data/data/com.termux/files/usr/bin/ifconfig
echo "✅ Done"

# Step 4
echo ""
echo "📦 Step 4/6: Installing OpenClaw..."
npm install -g openclaw@latest --ignore-scripts
echo "✅ Done"

# Step 5: Build koffi (required native module)
echo ""
echo "🔧 Step 5/6: Building native module..."
OPENCLAW_DIR="$(npm root -g)/openclaw"
cd "$OPENCLAW_DIR"
npm rebuild koffi
cd ~
echo "✅ Done"

# Step 6
echo ""
echo "📥 Step 6/6: Downloading scripts..."
REPO="https://raw.githubusercontent.com/orailnoor/orailnoor-CloudBot-Termux/main"
curl -sL "$REPO/phone_control.sh" > ~/phone_control.sh && chmod +x ~/phone_control.sh
curl -sL "$REPO/phone_agent.sh" > ~/phone_agent.sh && chmod +x ~/phone_agent.sh
mkdir -p ~/.openclaw/workspace
curl -sL "$REPO/AGENTS.md" > ~/.openclaw/workspace/AGENTS.md
echo "✅ Done"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 INSTALLATION COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Now run:"
echo "  1. openclaw onboard"
echo "  2. openclaw auth add google --key YOUR_KEY"
echo "  3. openclaw gateway --verbose"
echo ""
