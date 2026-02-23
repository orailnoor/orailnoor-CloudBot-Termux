#!/data/data/com.termux/files/usr/bin/bash

# Shizuku Setup Fix (Manual Install)
# Writes the rish wrapper manually to avoid download errors.

RISH_PATH="/data/data/com.termux/files/usr/bin/rish"

echo "Re-installing rish manually..."

# Create the rish script content directly
cat << 'EOF' > "$RISH_PATH"
#!/system/bin/sh
export CLASSPATH=/data/local/tmp/shizuku_starter:/data/app/moe.shizuku.privileged.api-1/base.apk
# Attempt to find Shizuku APK path dynamically if fixed path fails
if [ ! -f /data/app/moe.shizuku.privileged.api-1/base.apk ]; then
    APK_PATH=$(pm path moe.shizuku.privileged.api | cut -d: -f2)
    if [ -n "$APK_PATH" ]; then
        export CLASSPATH=$APK_PATH
    fi
fi
exec app_process /system/bin moe.shizuku.manager.shell.Shell "$@"
EOF

chmod +x "$RISH_PATH"

echo "✅ rish updated! Checking content:"
head -n 1 "$RISH_PATH"

echo ""
echo "Try running: rish input tap 500 500"
