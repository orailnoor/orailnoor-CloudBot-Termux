#!/data/data/com.termux/files/usr/bin/bash

# Define paths
DEPLOY_DIR="/sdcard/openclaw_deploy"
TERMUX_HOME="$HOME"
OPENCLAW_WS="$HOME/.openclaw/workspace"

echo "=== Deploying Phone Agent Files ==="

# Check if deploy dir exists
if [ ! -d "$DEPLOY_DIR" ]; then
    echo "❌ Error: Deploy directory '$DEPLOY_DIR' not found!"
    exit 1
fi

echo "📂 Source: $DEPLOY_DIR"
echo "📂 Dest:   $TERMUX_HOME"

# Copy files to home
echo "--> Copying core files..."
cp "$DEPLOY_DIR/phone_agent.py" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/phone_control.sh" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/system_prompt.txt" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/visual_agent.sh" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/connect.sh" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/switch_api.sh" "$TERMUX_HOME/"
cp "$DEPLOY_DIR/setup_openclaw.sh" "$TERMUX_HOME/"

# Copy AGENTS.md to workspace
if [ -d "$OPENCLAW_WS" ]; then
    echo "--> Updating AGENTS.md in workspace..."
    cp "$DEPLOY_DIR/AGENTS.md" "$OPENCLAW_WS/"
    echo "✅ Updated $OPENCLAW_WS/AGENTS.md"
else
    echo "⚠️ Warning: OpenClaw workspace not found at $OPENCLAW_WS"
    echo "   Copying AGENTS.md to home instead."
    cp "$DEPLOY_DIR/AGENTS.md" "$TERMUX_HOME/"
fi

# Set permissions
echo "--> Setting execute permissions..."
chmod +x "$TERMUX_HOME/phone_agent.py"
chmod +x "$TERMUX_HOME/phone_control.sh"
chmod +x "$TERMUX_HOME/visual_agent.sh"
chmod +x "$TERMUX_HOME/connect.sh"
chmod +x "$TERMUX_HOME/switch_api.sh"
chmod +x "$TERMUX_HOME/setup_openclaw.sh"

# Fix ownership if running as root (just in case)
if [ "$(id -u)" -eq 0 ]; then
    echo "--> Running as root, fixing ownership..."
    # Find Termux UID (usually starts with 10... e.g. 10145)
    # This is tricky without knowing it, usually unnecessary inside Termux.
    # Assuming standard Termux usage, files created by root in non-root dirs might need chown.
    # But typically users run this script AS the termux user.
    echo "   Skipping chown inside script."
fi

echo ""
echo "✅ Deployment Complete!"
echo "   Run: python3 ~/phone_agent.py \"Open YouTube\""
