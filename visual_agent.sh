#!/data/data/com.termux/files/usr/bin/bash
# ============================================
# Visual Phone Agent - Screenshot + Analyze + Act
# Takes a screenshot and sends it to Telegram
# so the AI can see the screen and decide actions
# ============================================

BOT_TOKEN="8525787791:AAEeUz5QirMkrOsDVjdElHddMUxLE1aS268"
CHAT_ID="1498653324"

ACTION="$1"
shift

case "$ACTION" in
  look)
    # Take screenshot and send to Telegram for AI to see
    FILENAME="/sdcard/screen_$(date +%s).png"
    su -c "screencap '$FILENAME'"
    
    # Send to Telegram so AI can analyze it
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
      -F "chat_id=${CHAT_ID}" \
      -F "photo=@${FILENAME}" \
      -F "caption=📸 Current screen state" > /dev/null
    
    echo "📸 Screenshot taken and sent to Telegram for analysis"
    echo "File: $FILENAME"
    ;;

  look-and-describe)
    # Take screenshot, save coordinates grid overlay
    FILENAME="/sdcard/screen_$(date +%s).png"
    su -c "screencap '$FILENAME'"
    
    # Get screen dimensions
    WIDTH=$(su -c "wm size" | grep -o '[0-9]*x[0-9]*' | cut -dx -f1)
    HEIGHT=$(su -c "wm size" | grep -o '[0-9]*x[0-9]*' | cut -dx -f2)
    
    echo "📸 Screenshot: $FILENAME"
    echo "📐 Screen: ${WIDTH}x${HEIGHT}"
    echo ""
    echo "Grid reference (approximate tap targets):"
    echo "┌──────┬──────┬──────┐"
    echo "│(180, │(540, │(900, │"
    echo "│ 370) │ 370) │ 370) │  ← Top"
    echo "├──────┼──────┼──────┤"
    echo "│(180, │(540, │(900, │"
    echo "│ 750) │ 750) │ 750) │  ← Upper"
    echo "├──────┼──────┼──────┤"
    echo "│(180, │(540, │(900, │"
    echo "│1120) │1120) │1120) │  ← Middle"
    echo "├──────┼──────┼──────┤"
    echo "│(180, │(540, │(900, │"
    echo "│1500) │1500) │1500) │  ← Lower"
    echo "├──────┼──────┼──────┤"
    echo "│(180, │(540, │(900, │"
    echo "│1870) │1870) │1870) │  ← Bottom"
    echo "└──────┴──────┴──────┘"
    echo ""
    echo "Navigation bar: (180,2150) (540,2150) (900,2150)"
    
    # Send to Telegram
    curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendPhoto" \
      -F "chat_id=${CHAT_ID}" \
      -F "photo=@${FILENAME}" \
      -F "caption=📸 Screen with grid - tell me what to tap" > /dev/null
    ;;

  do)
    # Execute a sequence of actions
    # Usage: visual_agent.sh do "tap 500 500" "wait 1" "type hello" "tap 900 2100"
    for step in "$@"; do
      ACTION_TYPE=$(echo "$step" | awk '{print $1}')
      ARGS=$(echo "$step" | cut -d' ' -f2-)
      
      case "$ACTION_TYPE" in
        tap)    su -c "input tap $ARGS" ;;
        swipe)  su -c "input swipe $ARGS" ;;
        type)   su -c "input text '$ARGS'" ;;
        key)    su -c "input keyevent $ARGS" ;;
        wait)   sleep "$ARGS" ;;
        home)   su -c "input keyevent 3" ;;
        back)   su -c "input keyevent 4" ;;
        *)      echo "Unknown: $step" ;;
      esac
      
      echo "✅ $step"
      sleep 0.3
    done
    echo "🏁 Sequence complete"
    ;;

  sequence)
    # Run a named automation sequence
    case "$1" in
      open-whatsapp-chat)
        CONTACT="$2"
        su -c "monkey -p com.whatsapp -c android.intent.category.LAUNCHER 1" 2>/dev/null
        sleep 2
        su -c "input tap 540 350"   # Search
        sleep 1
        su -c "input text '$CONTACT'"
        sleep 1
        su -c "input tap 540 450"   # First result
        sleep 1
        echo "📱 Opened WhatsApp chat with $CONTACT"
        ;;
      
      send-whatsapp)
        CONTACT="$2"
        shift 2
        MESSAGE="$*"
        su -c "monkey -p com.whatsapp -c android.intent.category.LAUNCHER 1" 2>/dev/null
        sleep 2
        su -c "input tap 540 350"   # Search
        sleep 1
        su -c "input text '$CONTACT'"
        sleep 1
        su -c "input tap 540 450"   # First result
        sleep 1
        su -c "input tap 700 2100"  # Message input
        sleep 0.5
        su -c "input text '$MESSAGE'"
        sleep 0.5
        su -c "input tap 980 2100"  # Send
        echo "📱 WhatsApp message sent to $CONTACT: $MESSAGE"
        ;;

      scroll-down)
        su -c "input swipe 540 1500 540 600 300"
        echo "⬇️ Scrolled down"
        ;;

      scroll-up)
        su -c "input swipe 540 600 540 1500 300"
        echo "⬆️ Scrolled up"
        ;;
    esac
    ;;

  *)
    echo "🤖 Visual Phone Agent Commands:"
    echo ""
    echo "  look                    - Screenshot → send to Telegram for AI to see"
    echo "  look-and-describe       - Screenshot + coordinate grid"
    echo "  do \"tap 500 500\" ...    - Execute action sequence"
    echo "  sequence open-whatsapp-chat <name> - Open WhatsApp chat"
    echo "  sequence send-whatsapp <name> <msg> - Send WhatsApp message"
    echo "  sequence scroll-down    - Scroll down"
    echo "  sequence scroll-up      - Scroll up"
    echo ""
    ;;
esac
