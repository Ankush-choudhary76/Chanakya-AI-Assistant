import sys
import os
from .config import CURRENT_OS, IS_MAC
from .agent import ChanakyaAgent
from .audio import SpeechToText

# ANSI Terminal Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BLUE = "\033[94m"
RED = "\033[91m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
   ██████╗██╗  ██╗ █████╗ ███╗   ██╗ █████╗ ██╗  ██╗██╗   ██╗ █████╗ 
  ██╔════╝██║  ██║██╔══██╗████╗  ██║██╔══██╗██║ ██╔╝╚██╗ ██╔╝██╔══██╗
  ██║     ███████║███████║██╔██╗ ██║███████║█████╔╝  ╚████╔╝ ███████║
  ██║     ██╔══██║██╔══██║██║╚██╗██║██╔══██║██╔═██╗   ╚██╔╝  ██╔══██║
  ╚██████╗██║  ██║██║  ██║██║ ╚████║██║  ██║██║  ██╗   ██║   ██║  ██║
   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═╝
{RESET}{YELLOW}   Chanakya — Personal AI Strategist & Desktop Assistant (macOS & Windows)
   Created & Maintained by Ankush Choudhary (github.com/Ankush-choudhary76)
{RESET}"""

def run_cli():
    print(BANNER)
    
    def log_handler(tag: str, msg: str):
        if tag == "TOOL":
            print(f"{YELLOW}⚡ [Action] {msg}{RESET}")
        elif tag == "TOOL_RESULT":
            print(f"{MAGENTA}✓ [Result] {msg}{RESET}")
        elif tag == "SONNY" and msg == "Thinking...":
            print(f"{CYAN}⏳ Chanakya is thinking...{RESET}")

    agent = ChanakyaAgent(on_log=log_handler)
    stt = SpeechToText()

    # System Status
    llm_status = f"{GREEN}Connected (Ollama: {agent.llm.model}){RESET}" if agent.llm.is_connected else f"{YELLOW}Offline Smart-Intent Mode{RESET}"
    tts_status = f"{GREEN}macOS Native (say){RESET}" if IS_MAC else f"{GREEN}Windows SAPI{RESET}"
    
    print(f"  {BOLD}Operating System:{RESET} {CURRENT_OS}")
    print(f"  {BOLD}LLM Engine:{RESET}       {llm_status}")
    print(f"  {BOLD}Speech Output:{RESET}    {tts_status}")
    print(f"  {BOLD}Commands:{RESET}         {CYAN}/voice{RESET} (toggle mic), {CYAN}/tools{RESET} (list tools), {CYAN}/memory{RESET} (view facts), {CYAN}/quit{RESET}\n")
    print(f"{BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{RESET}")

    voice_mode = False

    while True:
        try:
            prompt_symbol = f"{MAGENTA}[🎙️ Voice]{RESET} " if voice_mode else ""
            user_input = ""

            if voice_mode:
                user_input = stt.listen(timeout=5)
                if not user_input:
                    user_input = input(f"{GREEN}You:{RESET} ")
                else:
                    print(f"{GREEN}You (Voice):{RESET} {user_input}")
            else:
                user_input = input(f"{GREEN}You:{RESET} ")

            user_input = user_input.strip()
            if not user_input:
                continue

            # Command Handlers
            if user_input.lower() in ["/quit", "exit", "quit", "q"]:
                print(f"\n{CYAN}Chanakya: Alvida, Ankush! Have a productive day.{RESET}")
                agent.tts.speak("Goodbye, Ankush! Have a productive day.", async_mode=False)
                break

            if user_input.lower() == "/voice":
                voice_mode = not voice_mode
                status_str = "ENABLED (Speak your requests)" if voice_mode else "DISABLED (Type your requests)"
                print(f"{YELLOW}🎤 Voice Mode: {status_str}{RESET}")
                continue

            if user_input.lower() == "/tools":
                print(f"\n{YELLOW}{BOLD}Registered Chanakya Tools:{RESET}")
                for name, t in agent.tools.tools.items():
                    print(f"  • {BOLD}{name}{RESET}: {t['description']}")
                print()
                continue

            if user_input.lower() == "/memory":
                facts = agent.memory.get_all_facts()
                print(f"\n{MAGENTA}{BOLD}Stored Facts in Chanakya Memory:{RESET}")
                if not facts:
                    print("  (No facts saved yet. Tell me 'Remember that my favorite editor is VS Code')")
                else:
                    for f in facts:
                        print(f"  • {f}")
                print()
                continue

            if user_input.lower() == "/clear":
                agent.memory.clear()
                print(f"{YELLOW}Conversation memory cleared.{RESET}")
                continue

            # Process Assistant Response
            response = agent.process_input(user_input, voice_output=True)
            print(f"{CYAN}{BOLD}Chanakya:{RESET} {response}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n{CYAN}Chanakya: Session terminated.{RESET}")
            break
