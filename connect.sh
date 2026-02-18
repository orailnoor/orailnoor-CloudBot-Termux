#!/data/data/com.termux/files/usr/bin/bash

# OpenClaw Wireless Debugging Connector (Non-Root)
# Use this to pair and connect ADB directly on device.

echo -e "\n=== OpenClaw Wireless Connector ==="
echo "1. Ensure Wi-Fi is ON."
echo "2. Open Android Settings > Developer Options > Wireless Debugging."
echo "3. Enable 'Wireless Debugging'."
echo "4. Tap 'Pair device with pairing code'."
echo "5. KEEP THAT SCREEN OPEN (Use Split Screen with Termux)."

echo -e "\n--- STEP 1: PAIRING ---"
echo "Enter the IP address and Port from the pairing screen (e.g., 192.168.1.5:34555)"
read -p "Pairing Address (IP:PORT): " PAIR_ADDR
read -p "Pairing Code (6 digits): " PAIR_CODE

echo "Attempting to pair with $PAIR_ADDR..."
adb pair "$PAIR_ADDR" "$PAIR_CODE"

echo -e "\n--- STEP 2: CONNECTING ---"
echo "Check the main Wireless Debugging screen for the connect address."
read -p "Connect Address (IP:PORT): " CONNECT_ADDR

echo "Connecting to $CONNECT_ADDR..."
adb connect "$CONNECT_ADDR"

echo -e "\n--- STATUS ---"
adb devices
echo "If you see 'device', you are connected!"
