#!/data/data/com.termux/files/usr/bin/python3
"""
🤖 Autonomous Phone Agent for Android
Controls the phone like a human using: Screenshot → AI Vision → Actions → Repeat
Works like computer-use agents but for Android.

Usage:
  python3 phone_agent.py "Open YouTube and search lofi music"
  python3 phone_agent.py "Send WhatsApp message to Mom saying Hello"
  python3 phone_agent.py --notify "Open Instagram and like the first post"
"""

import subprocess
import base64
import json
import sys
import time
import os
import re
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

# === CONFIGURATION ===
MODEL = "gemini-2.5-flash-lite"
MAX_STEPS = 25
SCREENSHOT_PATH = "/sdcard/agent_screen.png"
SCREEN_WIDTH = 1080
SCREEN_HEIGHT = 2240

# Telegram config (for sending progress updates)
TELEGRAM_BOT_TOKEN = "8525787791:AAEeUz5QirMkrOsDVjdElHddMUxLE1aS268"
TELEGRAM_CHAT_ID = "1498653324"
SEND_TELEGRAM_UPDATES = False  # Set via --notify flag


def load_api_key():
    """Load API key from OpenClaw auth config"""
    auth_path = os.path.expanduser("~/.openclaw/agents/main/agent/auth-profiles.json")
    try:
        with open(auth_path) as f:
            data = json.load(f)
            return data["profiles"]["google:default"]["key"]
    except Exception:
        pass
    # Fallback: try environment variable
    return os.environ.get("GEMINI_API_KEY", "")


def run_root(cmd):
    """Run a command as root and return output"""
    try:
        result = subprocess.run(
            ["su", "-c", cmd],
            capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except subprocess.TimeoutExpired:
        print(f"  ⏰ Command timed out: {cmd[:50]}...")
        return ""
    except Exception as e:
        print(f"  ❌ Command failed: {e}")
        return ""


def take_screenshot():
    """Take a screenshot and return base64 PNG"""
    run_root(f"screencap -p {SCREENSHOT_PATH}")
    time.sleep(0.3)  # Small delay to ensure file is written
    
    # Verify file exists and has content
    try:
        with open(SCREENSHOT_PATH, "rb") as f:
            data = f.read()
            if len(data) < 1000:
                raise Exception(f"Screenshot too small ({len(data)} bytes)")
            return base64.b64encode(data).decode()
    except FileNotFoundError:
        # Sometimes screencap writes to a root-owned location
        run_root(f"cp {SCREENSHOT_PATH} /data/data/com.termux/files/home/screen.png")
        run_root("chmod 644 /data/data/com.termux/files/home/screen.png")
        with open(os.path.expanduser("~/screen.png"), "rb") as f:
            return base64.b64encode(f.read()).decode()


def get_ui_elements():
    """Dump UI hierarchy and extract interactive elements"""
    try:
        run_root("uiautomator dump /sdcard/ui.xml")
        time.sleep(0.5)
        xml = run_root("cat /sdcard/ui.xml")

        if not xml or len(xml) < 50:
            return []

        elements = []
        # Match all node attributes — flexible order
        node_pattern = (
            r'<node[^>]*?'
            r'text="(?P<text>[^"]*)"[^>]*?'
            r'resource-id="(?P<rid>[^"]*)"[^>]*?'
            r'class="(?P<cls>[^"]*)"[^>]*?'
            r'content-desc="(?P<desc>[^"]*)"[^>]*?'
            r'clickable="(?P<click>[^"]*)"[^>]*?'
            r'bounds="\[(?P<x1>\d+),(?P<y1>\d+)\]\[(?P<x2>\d+),(?P<y2>\d+)\]"'
        )

        for m in re.finditer(node_pattern, xml):
            text = m.group("text") or m.group("desc")
            rid = m.group("rid")
            clickable = m.group("click") == "true"
            x1, y1 = int(m.group("x1")), int(m.group("y1"))
            x2, y2 = int(m.group("x2")), int(m.group("y2"))
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

            if text or (clickable and rid):
                label = text if text else rid.split("/")[-1] if rid else ""
                elements.append({
                    "label": label,
                    "clickable": clickable,
                    "center": [cx, cy],
                    "bounds": [x1, y1, x2, y2],
                    "type": m.group("cls").split(".")[-1]
                })

        return elements
    except Exception as e:
        return []


def execute_action(action):
    """Execute a single action on the phone"""
    atype = action.get("action", "")

    if atype == "tap":
        x, y = int(action["x"]), int(action["y"])
        run_root(f"input tap {x} {y}")
        print(f"  👆 Tap ({x}, {y})")

    elif atype == "double_tap":
        x, y = int(action["x"]), int(action["y"])
        run_root(f"input tap {x} {y}")
        time.sleep(0.1)
        run_root(f"input tap {x} {y}")
        print(f"  👆👆 Double tap ({x}, {y})")

    elif atype == "long_press":
        x, y = int(action["x"]), int(action["y"])
        dur = int(action.get("duration", 800))
        run_root(f"input swipe {x} {y} {x} {y} {dur}")
        print(f"  👆 Long press ({x}, {y}) {dur}ms")

    elif atype == "swipe":
        x1, y1 = int(action["x1"]), int(action["y1"])
        x2, y2 = int(action["x2"]), int(action["y2"])
        dur = int(action.get("duration", 300))
        run_root(f"input swipe {x1} {y1} {x2} {y2} {dur}")
        print(f"  👆 Swipe ({x1},{y1})→({x2},{y2})")

    elif atype == "drag":
        x1, y1 = int(action["x1"]), int(action["y1"])
        x2, y2 = int(action["x2"]), int(action["y2"])
        dur = int(action.get("duration", 1000))
        run_root(f"input swipe {x1} {y1} {x2} {y2} {dur}")
        print(f"  🖐️ Drag ({x1},{y1})→({x2},{y2}) {dur}ms")

    elif atype == "type":
        text = action.get("text", "")
        # Escape special characters for shell
        escaped = text.replace(" ", "%s").replace("'", "\\'").replace('"', '\\"')
        escaped = escaped.replace("&", "\\&").replace("|", "\\|").replace(";", "\\;")
        escaped = escaped.replace("(", "\\(").replace(")", "\\)").replace("<", "\\<").replace(">", "\\>")
        run_root(f"input text '{escaped}'")
        print(f"  ⌨️ Type: {text}")

    elif atype == "clear_and_type":
        # Select all existing text and delete it first, then type new text
        run_root("input keyevent 29 --longpress")  # Ctrl+A select all
        time.sleep(0.1)
        run_root("input keyevent 67")  # Delete
        time.sleep(0.2)
        text = action.get("text", "")
        escaped = text.replace(" ", "%s").replace("'", "\\'")
        run_root(f"input text '{escaped}'")
        print(f"  ⌨️ Clear & Type: {text}")

    elif atype == "key":
        code = int(action.get("code", 0))
        names = {3: "HOME", 4: "BACK", 24: "VOL_UP", 25: "VOL_DOWN",
                 26: "POWER", 66: "ENTER", 187: "RECENTS", 82: "MENU",
                 61: "TAB", 67: "DEL", 122: "HOME_SCREEN", 111: "ESCAPE",
                 84: "SEARCH"}
        run_root(f"input keyevent {code}")
        print(f"  🔘 Key: {names.get(code, code)}")

    elif atype == "open_app":
        pkg = action.get("package", "")
        run_root(f"monkey -p {pkg} -c android.intent.category.LAUNCHER 1 2>/dev/null")
        print(f"  📱 Open: {pkg}")
        time.sleep(2)

    elif atype == "wait":
        secs = float(action.get("seconds", 1))
        print(f"  ⏳ Wait {secs}s")
        time.sleep(secs)

    elif atype == "scroll_down":
        run_root("input swipe 540 1600 540 600 300")
        print(f"  ⬇️ Scroll down")

    elif atype == "scroll_up":
        run_root("input swipe 540 600 540 1600 300")
        print(f"  ⬆️ Scroll up")

    elif atype == "go_home":
        run_root("input keyevent 3")
        print(f"  🏠 Home")

    elif atype == "go_back":
        run_root("input keyevent 4")
        print(f"  ◀️ Back")

    elif atype == "open_notifications":
        run_root("cmd statusbar expand-notifications")
        print(f"  🔔 Notifications opened")

    elif atype == "open_quick_settings":
        run_root("cmd statusbar expand-settings")
        print(f"  ⚙️ Quick settings opened")

    elif atype == "screenshot":
        ts = int(time.time())
        path = f"/sdcard/screenshot_{ts}.png"
        run_root(f"screencap -p {path}")
        print(f"  📸 Screenshot saved: {path}")

    elif atype == "done":
        msg = action.get("message", "Task completed")
        print(f"  ✅ {msg}")
        return "done"

    else:
        print(f"  ❓ Unknown action: {atype}")

    return "continue"


def send_telegram_photo(photo_path, caption=""):
    """Send a photo to Telegram for progress tracking"""
    if not SEND_TELEGRAM_UPDATES:
        return
    try:
        import subprocess
        subprocess.run([
            "curl", "-s", "-X", "POST",
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
            "-F", f"chat_id={TELEGRAM_CHAT_ID}",
            "-F", f"photo=@{photo_path}",
            "-F", f"caption={caption[:1024]}"
        ], capture_output=True, timeout=15)
    except Exception:
        pass


def send_telegram_message(text):
    """Send a text message to Telegram"""
    if not SEND_TELEGRAM_UPDATES:
        return
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = json.dumps({"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}).encode()
        req = Request(url, data=data, method="POST")
        req.add_header("Content-Type", "application/json")
        urlopen(req, timeout=10)
    except Exception:
        pass


SYSTEM_PROMPT = """You are an autonomous Android phone agent. You see screenshots of a phone screen (1080x2240 pixels) and decide actions to complete the user's task.

## HOW YOU WORK
1. You see a screenshot of the current screen + a list of UI elements
2. You analyze what's visible and plan your next move
3. You output 1-3 actions to take
4. The system executes your actions, takes a new screenshot, and shows it to you
5. You repeat until the task is complete

## AVAILABLE ACTIONS (use exact JSON format)
- {"action": "tap", "x": 540, "y": 500} — Tap at coordinates
- {"action": "double_tap", "x": 540, "y": 500} — Double tap
- {"action": "long_press", "x": 540, "y": 500, "duration": 800} — Long press
- {"action": "swipe", "x1": 540, "y1": 1500, "x2": 540, "y2": 500, "duration": 300} — Swipe
- {"action": "drag", "x1": 200, "y1": 800, "x2": 600, "y2": 400, "duration": 1000} — Drag
- {"action": "type", "text": "hello world"} — Type text (keyboard must be open)
- {"action": "clear_and_type", "text": "new text"} — Clear existing text then type new text
- {"action": "key", "code": 4} — Press key (3=HOME, 4=BACK, 66=ENTER, 84=SEARCH)
- {"action": "open_app", "package": "com.instagram.android"} — Launch app by package name
- {"action": "scroll_down"} — Scroll page down
- {"action": "scroll_up"} — Scroll page up
- {"action": "go_home"} — Go to home screen
- {"action": "go_back"} — Press back button
- {"action": "open_notifications"} — Open notification shade
- {"action": "open_quick_settings"} — Open quick settings panel
- {"action": "wait", "seconds": 2} — Wait for content to load
- {"action": "done", "message": "Description of what was accomplished"} — Task complete

## COMMON APP PACKAGES
- WhatsApp: com.whatsapp
- Instagram: com.instagram.android
- YouTube: com.google.android.youtube
- Chrome: com.android.chrome
- Camera: org.codeaurora.snapcam
- Settings: com.android.settings
- Phone/Dialer: com.android.dialer
- Messages: com.google.android.apps.messaging
- Gmail: com.google.android.gm
- Maps: com.google.android.apps.maps
- Play Store: com.android.vending
- Telegram: org.telegram.messenger
- Twitter/X: com.twitter.android
- Spotify: com.spotify.music
- Gallery/Photos: com.google.android.apps.photos

## SCREEN COORDINATE REFERENCE (1080x2240)
- Status bar: y < 80
- Top area: y ~ 200-400
- Upper area: y ~ 400-800
- Center: (540, 1120)
- Lower area: y ~ 1400-1800
- Bottom/Nav bar area: y > 2000
- Search bars are typically at top (y ~ 150-300)
- Send buttons are typically bottom-right

## IMPORTANT RULES
1. ALWAYS respond with valid JSON — no markdown, no explanation outside JSON
2. Take 1-3 actions per step (prefer fewer, be precise)
3. USE UI element coordinates when available — they are more accurate than guessing
4. After opening an app, ALWAYS wait 2-3 seconds for it to load
5. If a keyboard is visible, you CAN type. If not, tap an input field first
6. If you're stuck, try BACK or HOME and restart your approach
7. If you see a loading screen, wait
8. When the task is FULLY done, use the "done" action
9. Be PATIENT — some apps take time to load
10. CAREFULLY describe what you see in your "thought" — this helps with debugging

## RESPONSE FORMAT (strict JSON only)
{
  "thought": "I can see the YouTube home page with trending videos. I need to tap the search icon at the top right to search for lofi music.",
  "actions": [
    {"action": "tap", "x": 980, "y": 150}
  ]
}"""


def call_gemini(api_key, conversation_parts, retry_count=0):
    """Call Gemini Vision API with full conversation history"""
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={api_key}"

    payload = {
        "systemInstruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [{
            "parts": conversation_parts
        }],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 1024,
            "responseMimeType": "application/json"
        }
    }

    data = json.dumps(payload).encode()
    req = Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")

    try:
        with urlopen(req, timeout=60) as response:
            result = json.loads(response.read())

        text = result["candidates"][0]["content"]["parts"][0]["text"]
        text = text.strip()

        # Clean potential markdown wrapping
        if text.startswith("```"):
            text = re.sub(r'^```\w*\n?', '', text)
            text = re.sub(r'\n?```$', '', text)

        parsed = json.loads(text)

        # Normalize: ensure actions is a list
        if "actions" not in parsed:
            if "action" in parsed:
                parsed = {"thought": parsed.get("thought", ""), "actions": [parsed]}
            else:
                parsed = {"thought": "No valid action", "actions": [{"action": "done", "message": "Could not determine action"}]}

        return parsed

    except HTTPError as e:
        body = e.read().decode()[:500]
        print(f"  ❌ API Error {e.code}: {body[:200]}")
        
        if e.code == 429 or "RESOURCE_EXHAUSTED" in body:
            wait_time = min(10 * (retry_count + 1), 60)
            print(f"  ⏳ Rate limited. Waiting {wait_time}s...")
            time.sleep(wait_time)
            if retry_count < 3:
                return call_gemini(api_key, conversation_parts, retry_count + 1)
            return {"thought": "Rate limited, giving up", "actions": [{"action": "done", "message": "Rate limited by API"}]}
        
        if e.code == 400 and "payload size" in body.lower():
            # Conversation too long, trim old screenshots
            print("  ⚠️ Payload too large, trimming conversation history...")
            # Keep only the last 2 screenshot+text pairs
            trimmed = []
            image_count = 0
            for part in reversed(conversation_parts):
                if "inline_data" in part:
                    image_count += 1
                    if image_count > 2:
                        continue
                trimmed.insert(0, part)
            if retry_count < 2:
                return call_gemini(api_key, trimmed, retry_count + 1)
        
        return {"thought": f"API error: {e.code}", "actions": [{"action": "done", "message": f"API error {e.code}"}]}

    except json.JSONDecodeError:
        print(f"  ⚠️ Invalid JSON response: {text[:200]}")
        if retry_count < 2:
            print("  🔄 Retrying...")
            time.sleep(2)
            return call_gemini(api_key, conversation_parts, retry_count + 1)
        return {"thought": "Invalid response", "actions": [{"action": "wait", "seconds": 1}]}

    except (URLError, TimeoutError) as e:
        print(f"  ❌ Network error: {e}")
        if retry_count < 2:
            print("  🔄 Retrying in 5s...")
            time.sleep(5)
            return call_gemini(api_key, conversation_parts, retry_count + 1)
        return {"thought": "Network error", "actions": [{"action": "done", "message": "Network error"}]}

    except Exception as e:
        print(f"  ❌ Error: {e}")
        return {"thought": str(e), "actions": [{"action": "done", "message": str(e)}]}


def main():
    global SEND_TELEGRAM_UPDATES

    # Parse arguments
    args = sys.argv[1:]
    
    if "--notify" in args:
        SEND_TELEGRAM_UPDATES = True
        args.remove("--notify")
    
    if not args:
        print("🤖 Autonomous Phone Agent")
        print("━" * 40)
        print()
        print("Usage: python3 phone_agent.py [--notify] \"<task>\"")
        print()
        print("Options:")
        print("  --notify    Send progress screenshots to Telegram")
        print()
        print("Examples:")
        print('  python3 phone_agent.py "Open Instagram"')
        print('  python3 phone_agent.py "Open YouTube and search lofi music"')
        print('  python3 phone_agent.py "Send WhatsApp message to Mom saying hello"')
        print('  python3 phone_agent.py "Open Settings and enable Dark Mode"')
        print('  python3 phone_agent.py "Open Play Store and install Twitter"')
        print('  python3 phone_agent.py "Open Chrome and search for weather today"')
        print('  python3 phone_agent.py --notify "Open Camera and take a photo"')
        print()
        return

    task = " ".join(args)
    api_key = load_api_key()

    if not api_key:
        print("❌ No API key found!")
        print("Set GEMINI_API_KEY env var or configure OpenClaw.")
        return

    print()
    print("🤖 AUTONOMOUS PHONE AGENT")
    print("━" * 40)
    print(f"📋 Task: {task}")
    print(f"🧠 Model: {MODEL}")
    print(f"🔄 Max steps: {MAX_STEPS}")
    if SEND_TELEGRAM_UPDATES:
        print(f"📱 Telegram updates: ON")
    print("━" * 40)

    send_telegram_message(f"🤖 *Phone Agent Started*\n📋 Task: {task}\n🧠 Model: {MODEL}")

    # Build conversation as a growing list of parts
    # Each step adds: screenshot image + text context → AI response → action result
    conversation_parts = []
    history = []
    start_time = time.time()

    for step in range(1, MAX_STEPS + 1):
        print(f"\n{'─' * 40}")
        print(f"📸 STEP {step}/{MAX_STEPS}")
        print(f"{'─' * 40}")

        # 1. Take screenshot
        print("  📸 Capturing screen...")
        try:
            screenshot_b64 = take_screenshot()
        except Exception as e:
            print(f"  ❌ Screenshot failed: {e}")
            # Try once more
            time.sleep(1)
            try:
                screenshot_b64 = take_screenshot()
            except Exception:
                print("  ❌ Screenshot failed twice, aborting")
                break

        # 2. Get UI elements
        print("  🔍 Reading UI elements...")
        ui_elements = get_ui_elements()
        print(f"  📋 Found {len(ui_elements)} elements")

        # Build UI element text
        ui_text = ""
        if ui_elements:
            ui_text = "\n\n📋 INTERACTIVE UI ELEMENTS:\n"
            for i, elem in enumerate(ui_elements[:50]):
                click_tag = " ✓clickable" if elem["clickable"] else ""
                ui_text += (f"  [{i}] \"{elem['label']}\" ({elem['type']}) "
                           f"center=({elem['center'][0]},{elem['center'][1]}) "
                           f"bounds={elem['bounds']}{click_tag}\n")

        # Build history text
        history_text = ""
        if history:
            history_text = "\n\n📜 PREVIOUS ACTIONS:\n"
            for h in history[-6:]:  # Keep last 6 steps
                actions_desc = ", ".join(
                    f"{a.get('action', '?')}" + 
                    (f"({a.get('x','')},{a.get('y','')})" if 'x' in a else "") +
                    (f"(\"{a.get('text','')[:20]}\")" if 'text' in a else "")
                    for a in h.get("actions", [])
                )
                history_text += f"  Step {h['step']}: {h['thought'][:80]} → [{actions_desc}]\n"

        user_message = f"""🎯 TASK: {task}

📍 Step {step} of {MAX_STEPS}
⏱️ Elapsed: {int(time.time() - start_time)}s
{ui_text}{history_text}
Analyze the screenshot and decide the next action(s). Respond with JSON only."""

        # Add this step's screenshot and context to conversation
        # To manage payload size, only keep last 3 screenshots in conversation
        # but keep all text history
        if step > 4:
            # Remove older screenshots to save payload space, but keep text parts
            trimmed_parts = []
            img_count = 0
            for part in reversed(conversation_parts):
                if "inline_data" in part:
                    img_count += 1
                    if img_count > 2:
                        # Replace old screenshot with a placeholder text
                        trimmed_parts.insert(0, {"text": "[previous screenshot - removed to save space]"})
                        continue
                trimmed_parts.insert(0, part)
            conversation_parts = trimmed_parts

        conversation_parts.append({
            "inline_data": {
                "mimeType": "image/png",
                "data": screenshot_b64
            }
        })
        conversation_parts.append({"text": user_message})

        # 3. Ask AI
        print("  🧠 Analyzing with Gemini Vision...")
        response = call_gemini(api_key, conversation_parts)

        thought = response.get("thought", "...")
        actions = response.get("actions", [])

        print(f"  💭 {thought}")
        print()

        # Send Telegram update every 3rd step or on important actions
        if SEND_TELEGRAM_UPDATES and (step % 3 == 1 or step == 1):
            send_telegram_photo(
                SCREENSHOT_PATH,
                f"📸 Step {step}: {thought[:200]}"
            )

        # 4. Execute actions
        task_done = False
        for action in actions:
            result = execute_action(action)
            if result == "done":
                task_done = True
                break
            time.sleep(0.3)

        if task_done:
            # Take final screenshot and send to Telegram
            if SEND_TELEGRAM_UPDATES:
                time.sleep(1)
                try:
                    take_screenshot()
                    done_msg = actions[-1].get("message", "Task completed") if actions else "Done"
                    send_telegram_photo(SCREENSHOT_PATH, f"✅ DONE: {done_msg}")
                except Exception:
                    pass
            break

        # 5. Record history
        history.append({
            "step": step,
            "thought": thought,
            "actions": actions
        })

        # Add AI's response to conversation for context
        conversation_parts.append({"text": f"AI decided: {thought}\nActions taken: {json.dumps(actions)}"})

        # Brief pause for screen to update after actions
        time.sleep(1.0)

    else:
        print(f"\n⚠️ Reached max steps ({MAX_STEPS}). Task may be incomplete.")
        send_telegram_message(f"⚠️ Phone Agent reached max steps ({MAX_STEPS}) for task: {task}")

    elapsed = int(time.time() - start_time)
    print()
    print("━" * 40)
    print(f"🏁 Agent finished in {elapsed}s ({step} steps)")
    print("━" * 40)

    send_telegram_message(f"🏁 *Agent finished* in {elapsed}s ({step} steps)\n📋 Task: {task}")


if __name__ == "__main__":
    main()
