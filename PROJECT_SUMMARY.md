# 🤖 Project: Clawdbot (OpenClaw for Android)

## 🎯 Purpose
The goal of this project is to transform a standard Android device into a **fully autonomous AI agent**. By leveraging **OpenClaw**, **Termux**, and **Google Gemini Vision**, the agent is capable of "seeing" the screen and interacting with it like a human would—tapping, swiping, typing, and navigating through apps to complete complex tasks.

This is designed for power users, developers, and AI enthusiasts who want a private, mobile AI workstation that can manage their digital life directly from their pocket.

---

## ✅ What We Have Achieved So Far

### 1. Core Infrastructure
- **Termux Environment**: Successfully set up OpenClaw to run natively on Android within the Termux environment.
- **Root/ADB Control**: Established a reliable way to execute privileged commands (taps, swipes, app launches) using `su -c`.
- **OpenClaw Gateway**: Configured the gateway to handle requests from multiple channels (Web Dashboard & Telegram).

### 2. The Visual Agent (`phone_agent.py`) 👁️
- **Advanced Vision Loop**: Developed a Python-powered agent that takes screenshots, identifies UI elements via `uiautomator`, and sends them to Gemini 2.5 Flash Lite for decision-making.
- **Multi-Turn Intelligence**: The agent now remembers previous screenshots and actions, allowing it to "understand" state changes (e.g., knowing that a search bar is now open).
- **Telegram Live Updates**: Added a `--notify` mode where the agent sends its "thoughts" and "vision" screenshots directly to Telegram as it works.
- **Robust Error Handling**: Implemented retries for rate limits, payload size management, and screenshot recovery.

### 3. Smart Orchestration (`AGENTS.md`) 🧠
- **Decision Logic**: Created a clear hierarchy for the AI. It now knows when to use "Quick Commands" for simple toggles (like WiFi) and when to deploy the "Visual Agent" for complex tasks (like searching YouTube).
- **Strict Guardrails**: Prevented common AI failures by forbidding noisy commands like `am start` in favor of more silent, reliable tools like `monkey`.

### 4. Direct Deployment Utility
- **One-Click Deploy**: Created `deploy_phone_agent.sh` and ADB-based triggers to instantly push updates from a developer machine (PC/Mac) to the phone's Termux home and OpenClaw workspace.

---

## 🛠️ Technical Stack
- **AI Model**: Google Gemini 2.5 Flash Lite (Low latency, high performance & cost-effective).
- **Hosting**: Termux (Android).
- **Communication**: Telegram Bot API / OpenClaw Web Dashboard.
- **Execution**: Python 3, Bash, ADB, and Shizuku/Root.

---

## 🎥 YouTube Video Roadmap
1. **Introduction**: Show the Clawdbot logo and the phone on a desk.
2. **The Goal**: "An AI that actually uses your phone for you."
3. **Setup**: Briefly show Termux and the OpenClaw dashboard.
4. **The "Wow" Demo**:
   - Ask Telegram: *"Open YouTube and play some lofi music."*
   - Show the phone screen moving automatically.
   - Show the Telegram notifications receiving the screenshots.
5. **Behind the Scenes**: Briefly explain the Vision Loop (Screen -> AI -> Tap).
6. **Closing**: Why local AI on mobile is the future.

---

## 🚀 Status: Production Ready
The system is now configured to handle most apps (WhatsApp, YouTube, Instagram, Settings) autonomously. The environment is optimized for the Poco F1 running Android 15.
