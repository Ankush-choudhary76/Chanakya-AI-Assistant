import urllib.request
import json
import re
from typing import Dict, Any, List, Optional
from .config import OLLAMA_BASE_URL, DEFAULT_MODEL, SYSTEM_PROMPT

class LLMEngine:
    """Local LLM Engine interfacing with Ollama or local inference endpoint with built-in fallback parser"""
    def __init__(self, base_url: str = OLLAMA_BASE_URL, model: str = DEFAULT_MODEL):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.is_connected = False
        self.check_connection()

    def check_connection(self) -> bool:
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags", headers={"User-Agent": "Sonny"})
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                data = json.loads(resp.read().decode())
                models = [m.get("name") for m in data.get("models", [])]
                self.is_connected = True
                if models and not any(self.model in m for m in models):
                    self.model = models[0]  # auto-select installed model
                return True
        except Exception:
            self.is_connected = False
            return False

    def query(self, messages: List[Dict[str, str]], tools_schema: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Query Ollama or use local rule-based intent engine"""
        if self.is_connected or self.check_connection():
            try:
                payload = {
                    "model": self.model,
                    "messages": messages,
                    "stream": False,
                    "tools": tools_schema
                }
                data_bytes = json.dumps(payload).encode("utf-8")
                req = urllib.request.Request(
                    f"{self.base_url}/api/chat",
                    data=data_bytes,
                    headers={"Content-Type": "application/json"}
                )
                with urllib.request.urlopen(req, timeout=30) as resp:
                    res_json = json.loads(resp.read().decode())
                    msg = res_json.get("message", {})
                    tool_calls = msg.get("tool_calls", [])
                    return {
                        "content": msg.get("content", ""),
                        "tool_calls": tool_calls
                    }
            except Exception as e:
                pass  # Fall back to heuristic engine

        # Fallback Heuristic Intent Engine (Works even when offline/Ollama is not running)
        last_user_msg = ""
        for m in reversed(messages):
            if m["role"] == "user":
                last_user_msg = m["content"].lower()
                break

        return self._heuristic_fallback(last_user_msg)

    def _heuristic_fallback(self, text: str) -> Dict[str, Any]:
        """Fast offline rule-based parser that executes tools without an active LLM daemon"""
        tool_calls = []

        # YouTube playback
        yt_match = re.search(r"(?:play|song|video|youtube)\s+(.+)", text)
        if yt_match and not "volume" in text:
            query = yt_match.group(1).replace("on youtube", "").strip()
            tool_calls.append({
                "function": {
                    "name": "youtube_play",
                    "arguments": {"query": query}
                }
            })
            return {"content": f"Opening YouTube to play '{query}'.", "tool_calls": tool_calls}

        # Web search
        search_match = re.search(r"(?:search|google|find)\s+(.+)", text)
        if search_match and not any(w in text for w in ["youtube", "battery", "volume"]):
            query = search_match.group(1).replace("on google", "").replace("on web", "").strip()
            tool_calls.append({
                "function": {
                    "name": "web_search",
                    "arguments": {"query": query}
                }
            })
            return {"content": f"Searching the web for '{query}'.", "tool_calls": tool_calls}

        # Battery
        if any(w in text for w in ["battery", "charge", "charging"]):
            tool_calls.append({
                "function": {
                    "name": "get_battery_status",
                    "arguments": {}
                }
            })
            return {"content": "Checking battery level.", "tool_calls": tool_calls}

        # Volume
        vol_match = re.search(r"(?:volume|sound)\s+(?:to\s+)?(\d+)", text)
        if vol_match:
            level = int(vol_match.group(1))
            tool_calls.append({
                "function": {
                    "name": "set_volume",
                    "arguments": {"level": level}
                }
            })
            return {"content": f"Setting volume to {level}%.", "tool_calls": tool_calls}

        # Launch App
        app_match = re.search(r"(?:open|launch)\s+([a-zA-Z0-9\s]+)", text)
        if app_match and not any(w in text for w in ["youtube", "url", "website", "http"]):
            app = app_match.group(1).strip()
            tool_calls.append({
                "function": {
                    "name": "launch_app",
                    "arguments": {"app_name": app}
                }
            })
            return {"content": f"Opening {app}.", "tool_calls": tool_calls}

        # Remember
        rem_match = re.search(r"(?:remember|save)\s+(?:that\s+)?(.+)", text)
        if rem_match:
            fact = rem_match.group(1).strip()
            tool_calls.append({
                "function": {
                    "name": "remember_fact",
                    "arguments": {"fact": fact}
                }
            })
            return {"content": f"Remembering: {fact}", "tool_calls": tool_calls}

        # Recall
        if any(w in text for w in ["what do you remember", "what is my", "recall", "stored facts"]):
            tool_calls.append({
                "function": {
                    "name": "recall_memory",
                    "arguments": {"query": text}
                }
            })
            return {"content": "Searching memory.", "tool_calls": tool_calls}

        # Screenshot
        if "screenshot" in text:
            tool_calls.append({
                "function": {
                    "name": "take_screenshot",
                    "arguments": {}
                }
            })
            return {"content": "Taking screenshot.", "tool_calls": tool_calls}

        # Math / Calculate
        calc_match = re.search(r"(?:calculate|what is|compute)\s+([0-9\+\-\*\/\(\)\s\.\%]+)", text)
        if calc_match:
            expr = calc_match.group(1).strip()
            tool_calls.append({
                "function": {
                    "name": "calculate",
                    "arguments": {"expression": expr}
                }
            })
            return {"content": f"Calculating {expr}.", "tool_calls": tool_calls}

        # Default conversational greeting / reply
        if any(w in text for w in ["hello", "hi", "hey", "namaste", "pranam"]):
            return {"content": "Namaste! I am Chanakya, your personal AI strategist and desktop assistant. How can I assist you with your computer today?", "tool_calls": []}

        if any(w in text for w in ["who are you", "what are you", "what is your name"]):
            return {"content": "I am Chanakya, a desktop AI assistant created by Ankush Choudhary. I can control your computer, search the web, play media, and remember key information.", "tool_calls": []}

        return {
            "content": f"I heard: '{text}'. (Connect Ollama for natural-language reasoning, or ask me to play music on YouTube, search the web, set volume, check battery, launch apps, or remember facts!)",
            "tool_calls": []
        }
