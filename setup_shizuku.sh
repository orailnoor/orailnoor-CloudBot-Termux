#!/data/data/com.termux/files/usr/bin/bash

# Shizuku Setup for Termux (rish)
# Allows running ADB commands via Shizuku app (No Root required if enabled via Wireless Debugging)

echo "Setting up Shizuku (rish)..."

# Download rish executable from official repo
echo "Downloading rish..."
curl -L "https://github.com/RikkaApps/Shizuku/releases/latest/download/rish" -o /data/data/com.termux/files/usr/bin/rish

# Make executable
chmod +x /data/data/com.termux/files/usr/bin/rish

echo ""
echo "✅ Shizuku (rish) installed!"
echo "Usage: rish <command>"
echo "Example: rish input tap 500 500"
echo ""
echo "⚠️  Ensure Shizuku app is running and authorized for Termux!"
