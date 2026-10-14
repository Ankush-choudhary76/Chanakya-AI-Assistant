import os
import platform
from pathlib import Path

# System Platform Detection
CURRENT_OS = platform.system()  # 'Darwin' for macOS, 'Windows' for Windows, 'Linux' for Linux
IS_MAC = CURRENT_OS == "Darwin"
IS_WINDOWS = CURRENT_OS == "Windows"
IS_LINUX = CURRENT_OS == "Linux"

# Base Data Directories
HOME_DIR = Path.home()
CHANAKYA_DATA_DIR = HOME_DIR / ".chanakya"
CHANAKYA_DATA_DIR.mkdir(parents=True, exist_ok=True)

MEMORY_FILE = CHANAKYA_DATA_DIR / "memory.json"
CAPTURES_DIR = CHANAKYA_DATA_DIR / "captures"
CAPTURES_DIR.mkdir(parents=True, exist_ok=True)

# LLM Settings
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
DEFAULT_MODEL = os.getenv("CHANAKYA_MODEL", "llama3.2")
SYSTEM_PROMPT = """You are Chanakya, a wise, fast, and highly capable AI personal strategist and desktop assistant created by Ankush Choudhary.
You can hear, speak, control the computer, browse the web, play media, remember information, and execute system tools seamlessly.
Respond clearly, strategically, and concisely.
Always use your available tools whenever an action (search, browser, app launch, volume, memory, etc.) is needed.
"""

# Voice & Persona Settings
ASSISTANT_NAME = "Chanakya"
WAKE_WORD = "chanakya"
VOICE_RATE = 180
VOICE_VOLUME = 1.0
