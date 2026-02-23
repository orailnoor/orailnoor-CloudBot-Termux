#!/data/data/com.termux/files/usr/bin/bash

echo "========================================="
echo "  OpenClaw Setup for Android (Termux)"
echo "========================================="
echo ""

# Step 1: Update packages
echo "[1/5] Updating Termux packages..."
pkg update -y
pkg upgrade -y

# Step 2: Install Node.js and Git
echo "[2/5] Installing Node.js and Git..."
pkg install -y nodejs git

echo "Node version: $(node -v)"
echo "NPM version: $(npm -v)"
echo "Git version: $(git --version)"

# Step 3: Install OpenClaw
echo "[3/5] Installing OpenClaw..."
npm install -g openclaw@2026.2.19

echo "OpenClaw version: $(openclaw --version 2>/dev/null || echo 'install may have failed')"

# Step 4: Fix Android Network Interface Error
echo "[4/5] Fixing Android network interface error..."
cat <<'EOF' > $HOME/hijack.js
const os = require('os');
os.networkInterfaces = () => ({});
EOF

# Add to bashrc if not already there
if ! grep -q "hijack.js" $HOME/.bashrc 2>/dev/null; then
    echo 'export NODE_OPTIONS="-r $HOME/hijack.js"' >> $HOME/.bashrc
fi
source $HOME/.bashrc

# Step 5: Done
echo ""
echo "========================================="
echo "  Setup Complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "  1. Run: openclaw onboard"
echo "     (Enter your Gemini API key when prompted)"
echo "     (Choose 127.0.0.1 for Gateway Bind)"
echo ""
echo "  2. Run: openclaw gateway --verbose"
echo "     (Starts the AI agent server)"
echo ""
echo "  3. Open browser: http://127.0.0.1:18789"
echo ""
 