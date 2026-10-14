# 🏛️ Chanakya — Personal AI Strategist & Desktop Assistant

<p align="center">
  <img src="resources/images/logo.png" alt="Chanakya AI Logo" width="200">
</p>

<p align="center">
  <strong>A local-first, cross-platform desktop AI assistant with voice, web search, browser automation, system control, and memory — engineered for macOS & Windows.</strong>
</p>

<p align="center">
  <img src="resources/images/banner.png" alt="Chanakya AI Desktop Showcase" width="800">
</p>

<p align="center">
  <a href="https://github.com/Ankush-choudhary76/Chanakya-AI-Assistant/stargazers"><img src="https://img.shields.io/badge/Maintained%20by-Ankush%20Choudhary-orange.svg" alt="Maintainer"></a>
  <a href="https://github.com/Ankush-choudhary76"><img src="https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-blue.svg" alt="Platform"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License"></a>
  <img src="https://img.shields.io/badge/Python-3.9%2B-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Voice-Always%20Listening-red.svg" alt="Voice">
</p>

---

## 🌟 Why Chanakya?

Most AI assistants can only **chat in a browser tab**.

**Chanakya is built to ACT and execute on your machine — just say its name:**

- *"Chanakya, play lo-fi beats on YouTube."*
- *"Chanakya, set the volume to 40%."*
- *"Chanakya, check my laptop battery."*
- *"Chanakya, remember that I prefer VS Code."*
- *"Chanakya, search the web for the latest AI research."*
- *"Chanakya, open Google Chrome."*
- *"Chanakya, take a screenshot."*

Chanakya executes those commands directly into actions through a unified tool-calling system on both **macOS** and **Windows**.

---

## 🎙️ Wake Word — Like Siri!

Chanakya supports an **always-listening Siri-style voice mode**.

Just say **"Chanakya"** — and it wakes up, listens, and responds by voice.

```
You say:    "Chanakya..."
🔔 Beep!
You say:    "Battery check karo"
🏛️ Chanakya: "Battery is at 87%, currently discharging."
```

Or combine in one sentence:
```
"Chanakya, play lofi music on YouTube"
"Chanakya, set volume to 60"
"Chanakya, search AI news"
```

---

## 🚀 Quick Start (Works on Mac & Windows Instantly)

### 1. Clone
```bash
git clone https://github.com/Ankush-choudhary76/Chanakya-AI-Assistant.git
cd Chanakya-AI-Assistant
```

### 2. Install Voice Dependencies (Optional but recommended for Siri mode)
```bash
# macOS
brew install portaudio
pip3 install SpeechRecognition pyaudio

# Windows
pip install SpeechRecognition pyaudio
```

### 3. Run — Choose your mode!

| Mode | Command | Description |
|:---|:---|:---|
| 🎙️ **Siri Mode** (Recommended) | `python3 main.py --siri` | Say "Chanakya" to activate — just like Siri! |
| 🌐 **Web Dashboard** | `python3 main.py --web` | Futuristic browser UI with mic button |
| 💻 **Terminal CLI** | `python3 main.py` | Type commands in terminal |

---

## 🎮 Running on macOS (One-Click)
```bash
chmod +x run.sh
./run.sh          # Terminal mode
./run.sh --siri   # Siri-style voice mode
./run.sh --web    # Web dashboard
```

## 🪟 Running on Windows (One-Click)
```cmd
run.bat           # Terminal mode
run.bat --siri    # Siri-style voice mode
run.bat --web     # Web dashboard
```

---

## 🏗️ Architecture

```text
                    YOU (Voice / Text)
                          │
                          ▼
   ┌────────────────────────────────────────────────────────┐
   │                    CHANAKYA AI                         │
   │                                                        │
   │   ┌────────────────────────────────────────────────┐   │
   │   │  🎙️ Voice Mode (Siri-style)                    │   │
   │   │   • Always-Listening Wake Word ("Chanakya")    │   │
   │   │   • Google Speech-to-Text                      │   │
   │   │   • macOS native TTS ('say') / Windows SAPI    │   │
   │   └────────────────────────────────────────────────┘   │
   │                                                        │
   │   ┌────────────────────────────────────────────────┐   │
   │   │  🍏 Cross-Platform Engine (macOS & Windows)    │   │
   │   │   • Python 3.9+ Runtime                        │   │
   │   │   • Ollama / Local LLM + Smart Fallback        │   │
   │   │   • 12+ System Tools                           │   │
   │   │   • Local Memory (RAG) at ~/.chanakya/         │   │
   │   └────────────────────────────────────────────────┘   │
   │                                                        │
   │   ┌────────────────────────────────────────────────┐   │
   │   │  🪟 Native C++ Engine (Windows Only)           │   │
   │   │   • llama.cpp + GGUF LLM inference             │   │
   │   │   • DirectX 11 3D Avatar Overlay               │   │
   │   │   • WASAPI Audio Pipeline                      │   │
   │   └────────────────────────────────────────────────┘   │
   └────────────────────────┬───────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────────┐
          ▼                 ▼                     ▼
       Browser           System               Memory
   • YouTube          • Volume/Battery     • Fact Storing
   • Web Search       • App Launcher       • RAG Recall
   • URL Navigation   • Screenshot         • ~/.chanakya/
```

---

## ✨ Key Capabilities

| Feature | Capability | macOS | Windows |
| :--- | :--- | :---: | :---: |
| 🎙️ **Siri-style Voice** | Say "Chanakya" to activate — always listening | ✅ | ✅ |
| 🔊 **Voice Output** | Natural spoken responses | ✅ macOS `say` | ✅ SAPI |
| 🌐 **Browser Control** | YouTube, Google search, URL navigation | ✅ | ✅ |
| 💻 **System Control** | Volume, battery, app launch, clipboard | ✅ | ✅ |
| 📸 **Screenshot** | Instant screen capture | ✅ | ✅ |
| 💾 **Local Memory** | Permanent fact recall (`~/.chanakya/`) | ✅ | ✅ |
| 🖥️ **Web Dashboard** | Premium futuristic browser UI | ✅ | ✅ |

---

## 🧠 Connecting Local LLM (Optional — for deeper reasoning)

1. Install [Ollama](https://ollama.com/)
2. Run any model:
   ```bash
   ollama run llama3.2
   ```
3. Chanakya auto-detects Ollama at `http://localhost:11434` and uses it for natural language queries.

> Without Ollama, Chanakya uses its built-in **Smart Intent Engine** to handle common commands offline.

---

## 🛠️ CLI Commands (Terminal Mode)

| Command | Action |
|:---|:---|
| `/voice` | Toggle microphone voice recognition |
| `/tools` | List all available tools |
| `/memory` | View stored facts |
| `/clear` | Clear conversation |
| `/quit` | Exit |

---

## 📦 Native Windows C++ Build (Optional)

For maximum performance on Windows with DirectX 11 3D avatar:
```cmd
cmake.bat
build.bat
```
*Requires Visual Studio 2022 with C++ desktop workload.*

---

## 👤 Author

**Ankush Choudhary**
- GitHub: [@Ankush-choudhary76](https://github.com/Ankush-choudhary76)

---

## 📄 License

This project is open-sourced under the [MIT License](LICENSE).
