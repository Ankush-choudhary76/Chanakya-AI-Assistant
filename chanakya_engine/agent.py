from typing import Dict, Any, List, Callable, Optional
from .config import SYSTEM_PROMPT
from .memory import MemoryStore
from .tools import ToolRegistry
from .llm import LLMEngine
from .audio import TextToSpeech

class ChanakyaAgent:
    """Core Assistant Orchestrator managing memory, tools, LLM, and speech"""
    def __init__(self, on_log: Optional[Callable[[str, str], None]] = None):
        self.memory = MemoryStore()
        self.tools = ToolRegistry(self.memory)
        self.llm = LLMEngine()
        self.tts = TextToSpeech()
        self.on_log = on_log or (lambda tag, msg: None)

        self.messages: List[Dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

        # Load recent context facts into system prompt
        facts = self.memory.get_all_facts()
        if facts:
            facts_summary = "\nKnown user facts:\n" + "\n".join(f"- {f}" for f in facts[-10:])
            self.messages[0]["content"] += facts_summary

    def log(self, tag: str, msg: str):
        self.on_log(tag, msg)

    def process_input(self, user_text: str, voice_output: bool = True) -> str:
        """Process user input, query LLM, execute required tools, and return final response"""
        user_text = user_text.strip()
        if not user_text:
            return ""

        self.log("USER", user_text)
        self.messages.append({"role": "user", "content": user_text})
        self.memory.add_history("user", user_text)

        # Query LLM / Heuristic Engine
        self.log("SONNY", "Thinking...")
        tools_schema = self.tools.get_schemas()
        response_data = self.llm.query(self.messages, tools_schema)

        tool_calls = response_data.get("tool_calls", [])
        content = response_data.get("content", "")

        # Execute Tool Calls
        tool_results_text = []
        if tool_calls:
            for tc in tool_calls:
                func_data = tc.get("function", {})
                tool_name = func_data.get("name", "")
                tool_args = func_data.get("arguments", {})
                if isinstance(tool_args, str):
                    try:
                        import json
                        tool_args = json.loads(tool_args)
                    except Exception:
                        tool_args = {}

                self.log("TOOL", f"Executing {tool_name}({tool_args})")
                tool_res = self.tools.execute(tool_name, tool_args)
                self.log("TOOL_RESULT", f"{tool_name} -> {tool_res}")
                tool_results_text.append(f"[{tool_name}]: {tool_res}")

        final_response = content
        if tool_results_text:
            if final_response:
                final_response += "\n" + "\n".join(tool_results_text)
            else:
                final_response = "\n".join(tool_results_text)

        self.log("SONNY", final_response)
        self.messages.append({"role": "assistant", "content": final_response})
        self.memory.add_history("assistant", final_response)

        # Speak Response
        if voice_output and final_response:
            # Speak only the friendly part, skip verbose command outputs
            spoken_part = content if content else tool_results_text[0] if tool_results_text else ""
            self.tts.speak(spoken_part)

        return final_response
