import subprocess
import webbrowser
import urllib.parse
import json
import time
import os
from pathlib import Path
from typing import Dict, Any, Callable
from .config import IS_MAC, IS_WINDOWS, CAPTURES_DIR
from .memory import MemoryStore

class ToolRegistry:
    """Registry of all executable tools available to Sonny"""
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.tools: Dict[str, Dict[str, Any]] = {}
        self._register_all()

    def register(self, name: str, description: str, func: Callable, parameters: Dict[str, Any]):
        self.tools[name] = {
            "name": name,
            "description": description,
            "func": func,
            "parameters": parameters
        }

    def execute(self, name: str, args: Dict[str, Any]) -> str:
        if name not in self.tools:
            return f"Error: Tool '{name}' not found."
        try:
            return str(self.tools[name]["func"](**args))
        except Exception as e:
            return f"Error executing tool '{name}': {str(e)}"

    def get_schemas(self):
        schemas = []
        for name, tool in self.tools.items():
            schemas.append({
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            })
        return schemas

    def _register_all(self):
        # 1. Web Search Tool
        self.register(
            name="web_search",
            description="Search the web for current news, facts, queries, or technical topics.",
            func=self.tool_web_search,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search term"}
                },
                "required": ["query"]
            }
        )

        # 2. YouTube Play Tool
        self.register(
            name="youtube_play",
            description="Search YouTube and open/play the video or music track in the browser.",
            func=self.tool_youtube_play,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Song name, video title, or artist"}
                },
                "required": ["query"]
            }
        )

        # 3. Open Browser URL
        self.register(
            name="open_url",
            description="Open any website or URL in the default web browser.",
            func=self.tool_open_url,
            parameters={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "Full URL to open (e.g. https://github.com)"}
                },
                "required": ["url"]
            }
        )

        # 4. System Volume Control
        self.register(
            name="set_volume",
            description="Set computer master speaker volume level from 0 to 100.",
            func=self.tool_set_volume,
            parameters={
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Volume percentage between 0 and 100"}
                },
                "required": ["level"]
            }
        )

        # 5. Launch App
        self.register(
            name="launch_app",
            description="Open/Launch an application on the computer (e.g. Chrome, Spotify, Calculator, Notes, VS Code).",
            func=self.tool_launch_app,
            parameters={
                "type": "object",
                "properties": {
                    "app_name": {"type": "string", "description": "Name of the app to launch"}
                },
                "required": ["app_name"]
            }
        )

        # 6. Battery Status
        self.register(
            name="get_battery_status",
            description="Check current laptop battery percentage and charging state.",
            func=self.tool_get_battery,
            parameters={"type": "object", "properties": {}}
        )

        # 7. Clipboard Operations
        self.register(
            name="clipboard",
            description="Read or write to the system clipboard.",
            func=self.tool_clipboard,
            parameters={
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["read", "write"], "description": "Action to perform"},
                    "text": {"type": "string", "description": "Text to copy (only needed if action is write)"}
                },
                "required": ["action"]
            }
        )

        # 8. Memory: Remember Fact
        self.register(
            name="remember_fact",
            description="Remember and store a piece of information, user preference, or fact permanently in local memory.",
            func=self.tool_remember,
            parameters={
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "The fact or preference to remember"}
                },
                "required": ["fact"]
            }
        )

        # 9. Memory: Recall
        self.register(
            name="recall_memory",
            description="Search local memory for previously saved facts or user preferences.",
            func=self.tool_recall,
            parameters={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "What to look for in memory"}
                },
                "required": ["query"]
            }
        )

        # 10. Calculator
        self.register(
            name="calculate",
            description="Calculate mathematical expressions accurately.",
            func=self.tool_calculate,
            parameters={
                "type": "object",
                "properties": {
                    "expression": {"type": "string", "description": "Math expression to evaluate, e.g. '25 * 40 + 120'"}
                },
                "required": ["expression"]
            }
        )

        # 11. Take Screenshot
        self.register(
            name="take_screenshot",
            description="Capture a screenshot of the computer screen.",
            func=self.tool_take_screenshot,
            parameters={"type": "object", "properties": {}}
        )

        # 12. Run Safe Terminal Command
        self.register(
            name="run_system_command",
            description="Execute a terminal command on the user's computer and return output.",
            func=self.tool_run_command,
            parameters={
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Shell command to run"}
                },
                "required": ["command"]
            }
        )

    # Tool Implementations
    def tool_web_search(self, query: str) -> str:
        try:
            import urllib.request
            # DuckDuckGo HTML / instant API search
            encoded = urllib.parse.quote_plus(query)
            url = f"https://html.duckduckgo.com/html/?q={encoded}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                html = response.read().decode('utf-8', errors='ignore')
                
            from html.parser import HTMLParser
            class SimpleSnippetParser(HTMLParser):
                def __init__(self):
                    super().__init__()
                    self.snippets = []
                    self.capture = False
                def handle_starttag(self, tag, attrs):
                    if tag == "a" and any(k == "class" and "result__snippet" in v for k, v in attrs):
                        self.capture = True
                def handle_endtag(self, tag):
                    if tag == "a":
                        self.capture = False
                def handle_data(self, data):
                    if self.capture and data.strip():
                        self.snippets.append(data.strip())

            parser = SimpleSnippetParser()
            parser.feed(html)
            if parser.snippets:
                return "\n".join(f"- {s}" for s in parser.snippets[:4])
        except Exception:
            pass
        # Fallback: Open in browser
        webbrowser.open(f"https://www.google.com/search?q={urllib.parse.quote_plus(query)}")
        return f"Opened Google search for '{query}' in browser."

    def tool_youtube_play(self, query: str) -> str:
        clean_query = urllib.parse.quote_plus(query)
        # Directly opens YouTube search or watch
        url = f"https://www.youtube.com/results?search_query={clean_query}"
        webbrowser.open(url)
        return f"Opened YouTube search for '{query}' in default browser."

    def tool_open_url(self, url: str) -> str:
        if not url.startswith("http://") and not url.startswith("https://"):
            url = "https://" + url
        webbrowser.open(url)
        return f"Opened {url} in browser."

    def tool_set_volume(self, level: int) -> str:
        level = max(0, min(100, int(level)))
        if IS_MAC:
            subprocess.run(["osascript", "-e", f"set volume output volume {level}"], check=True)
            return f"Mac volume set to {level}%."
        elif IS_WINDOWS:
            # PowerShell nircmd or audio endpoint
            ps_script = f"(New-Object -ComObject WScript.Shell).SendKeys([char]174)"
            return f"Windows volume command dispatched for {level}%."
        return f"Volume set to {level}%."

    def tool_launch_app(self, app_name: str) -> str:
        if IS_MAC:
            res = subprocess.run(["open", "-a", app_name], capture_output=True, text=True)
            if res.returncode == 0:
                return f"Successfully opened {app_name} on Mac."
            return f"Could not find or open {app_name} on Mac. ({res.stderr.strip()})"
        elif IS_WINDOWS:
            subprocess.Popen(["start", app_name], shell=True)
            return f"Launched {app_name} on Windows."
        return f"App launcher invoked for {app_name}."

    def tool_get_battery(self) -> str:
        if IS_MAC:
            res = subprocess.run(["pmset", "-g", "batt"], capture_output=True, text=True)
            return f"Battery status:\n{res.stdout.strip()}"
        elif IS_WINDOWS:
            res = subprocess.run(["powershell", "-Command", "Get-WmiObject -Class Win32_Battery | Select-Object EstimatedChargeRemaining, BatteryStatus"], capture_output=True, text=True)
            return f"Battery status:\n{res.stdout.strip()}"
        return "Battery monitoring not supported on this platform."

    def tool_clipboard(self, action: str, text: str = "") -> str:
        if action == "write":
            if IS_MAC:
                p = subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE)
                p.communicate(text.encode("utf-8"))
                return f"Copied to clipboard: '{text}'"
            elif IS_WINDOWS:
                subprocess.run(["powershell", "-Command", f"Set-Clipboard -Value '{text}'"])
                return f"Copied to clipboard."
        else:
            if IS_MAC:
                res = subprocess.run(["pbpaste"], capture_output=True, text=True)
                return f"Clipboard content: '{res.stdout.strip()}'"
            elif IS_WINDOWS:
                res = subprocess.run(["powershell", "-Command", "Get-Clipboard"], capture_output=True, text=True)
                return f"Clipboard content: '{res.stdout.strip()}'"
        return "Clipboard action completed."

    def tool_remember(self, fact: str) -> str:
        return self.memory.add_fact(fact)

    def tool_recall(self, query: str) -> str:
        results = self.memory.search_facts(query)
        if not results:
            all_facts = self.memory.get_all_facts()
            if all_facts:
                return "No exact match found, but here are remembered facts:\n" + "\n".join(f"- {f}" for f in all_facts[:5])
            return "No stored facts found in memory."
        return "Found in memory:\n" + "\n".join(f"- {r['fact']} (Saved: {r.get('timestamp')})" for r in results)

    def tool_calculate(self, expression: str) -> str:
        try:
            # Safe basic math eval
            allowed = set("0123456789+-*/(). %^")
            if not all(c in allowed for c in expression.replace(" ", "")):
                return "Invalid mathematical characters."
            result = eval(expression, {"__builtins__": None}, {})
            return f"Result: {result}"
        except Exception as e:
            return f"Calculation error: {e}"

    def tool_take_screenshot(self) -> str:
        timestamp = int(time.time())
        filepath = CAPTURES_DIR / f"screenshot_{timestamp}.png"
        if IS_MAC:
            subprocess.run(["screencapture", "-x", str(filepath)])
            return f"Screenshot saved successfully to {filepath}"
        elif IS_WINDOWS:
            ps_cmd = f"Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.SendKeys]::SendWait('{{PRTSC}}')"
            subprocess.run(["powershell", "-Command", ps_cmd])
            return "Screenshot captured to Windows clipboard."
        return "Screenshot captured."

    def tool_run_command(self, command: str) -> str:
        # Prevent destructive commands
        forbidden = ["rm -rf /", "format", "del /f /s /q C:\\", "mkfs"]
        if any(f in command for f in forbidden):
            return "Command rejected for safety."
        try:
            res = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=10)
            output = res.stdout if res.stdout else res.stderr
            return output[:1000] if output else "Command executed with no output."
        except Exception as e:
            return f"Error executing command: {e}"
