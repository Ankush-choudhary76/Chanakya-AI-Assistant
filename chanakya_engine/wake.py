"""
Chanakya Wake-Word & Continuous Voice Assistant
Works like Siri / Hey Google - always listening, responds by voice.
macOS: Uses native 'say' TTS + SpeechRecognition mic
"""

import threading
import time
import sys
import os
import subprocess

from .agent import ChanakyaAgent
from .audio import TextToSpeech
from .config import IS_MAC, WAKE_WORD

# ANSI Colors
CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
RESET = "\033[0m"

BANNER = f"""{CYAN}{BOLD}
  🏛️  CHANAKYA — Always Listening Mode
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Say "Chanakya" to wake me up, then give your command.
  Press Ctrl+C to exit.
{RESET}"""


class ChanakyaWakeAssistant:
    """Siri-style always-on voice assistant for Chanakya"""

    def __init__(self):
        self.agent = ChanakyaAgent()
        self.tts = TextToSpeech()
        self.is_processing = False
        self._init_stt()

    def _init_stt(self):
        """Initialize speech recognition"""
        try:
            import speech_recognition as sr
            self.sr = sr
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 300
            self.recognizer.dynamic_energy_threshold = True
            self.recognizer.pause_threshold = 0.8
            self.mic = sr.Microphone()
            # Calibrate ambient noise
            with self.mic as source:
                print(f"{YELLOW}⚙️  Calibrating microphone for ambient noise...{RESET}")
                self.recognizer.adjust_for_ambient_noise(source, duration=1.5)
            print(f"{GREEN}✅ Microphone ready!{RESET}")
            self.stt_available = True
        except Exception as e:
            print(f"{YELLOW}⚠️  Microphone not available: {e}{RESET}")
            print(f"Install with: pip3 install SpeechRecognition pyaudio")
            self.stt_available = False

    def listen_once(self, timeout=5, phrase_limit=8) -> str:
        """Listen for one utterance and transcribe it"""
        if not self.stt_available:
            return input(f"{GREEN}You (type):{RESET} ").strip()
        try:
            with self.mic as source:
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_limit)
            text = self.recognizer.recognize_google(audio, language="en-IN")
            return text.strip()
        except self.sr.WaitTimeoutError:
            return ""
        except self.sr.UnknownValueError:
            return ""
        except Exception:
            return ""

    def contains_wake_word(self, text: str) -> str:
        """Check if text contains wake word and return the command part"""
        text_lower = text.lower()
        for wake in ["chanakya", "chankya", "chanakia", "chanakaya"]:  # common misrecognitions
            if wake in text_lower:
                # Extract command after wake word
                idx = text_lower.find(wake) + len(wake)
                command = text[idx:].strip().lstrip(",. ")
                return command
        return ""

    def play_wake_chime(self):
        """Play a chime/beep to indicate Chanakya is listening"""
        if IS_MAC:
            try:
                subprocess.run(["osascript", "-e", 'beep 1'], capture_output=True)
            except Exception:
                pass

    def speak(self, text: str, async_mode=False):
        """Speak text using TTS"""
        self.tts.speak(text, async_mode=async_mode)

    def run(self):
        """Main always-listening loop"""
        print(BANNER)

        if not self.stt_available:
            print(f"{YELLOW}⚠️  Microphone unavailable. Running in TEXT mode (type your commands).{RESET}")
            print(f"{YELLOW}   Install: pip3 install SpeechRecognition pyaudio{RESET}\n")

        # Greet on startup
        greeting = "Namaste! Chanakya is ready. Say Chanakya followed by your command, or just speak after the beep."
        print(f"{CYAN}🏛️  Chanakya: {greeting}{RESET}\n")
        self.speak(greeting, async_mode=True)
        time.sleep(1)

        while True:
            try:
                if not self.stt_available:
                    # Text fallback mode
                    raw = input(f"{GREEN}You:{RESET} ").strip()
                    if not raw:
                        continue
                    if raw.lower() in ["quit", "exit", "bye"]:
                        self.speak("Goodbye!", async_mode=False)
                        break
                    command = self.contains_wake_word(raw) or raw
                    self._handle_command(command)
                    continue

                # Voice mode: listen for wake word in ambient stream
                print(f"{YELLOW}👂 Listening for 'Chanakya'...{RESET}", end="\r")
                raw = self.listen_once(timeout=6, phrase_limit=8)

                if not raw:
                    continue

                print(f"{GREEN}Heard:{RESET} {raw}")

                # Check for wake word
                command = self.contains_wake_word(raw)
                if command is None:
                    # Wake word not detected — keep listening silently
                    continue

                if command:
                    # Wake word + command in same utterance (e.g., "Chanakya what time is it")
                    self._handle_command(command)
                else:
                    # Just wake word — play chime and listen for command
                    self.play_wake_chime()
                    print(f"\n{CYAN}🏛️  Chanakya: {BOLD}Yes? I'm listening...{RESET}")
                    self.speak("Yes?", async_mode=False)

                    print(f"{YELLOW}🎙️  Speak your command...{RESET}")
                    command = self.listen_once(timeout=7, phrase_limit=12)
                    if command:
                        print(f"{GREEN}You said:{RESET} {command}")
                        self._handle_command(command)
                    else:
                        print(f"{YELLOW}(No command heard){RESET}")

            except KeyboardInterrupt:
                print(f"\n{CYAN}🏛️  Chanakya: Goodbye, Ankush! See you soon.{RESET}")
                self.speak("Goodbye! See you soon.", async_mode=False)
                break
            except Exception as e:
                print(f"{YELLOW}[Error] {e}{RESET}")
                time.sleep(0.5)

    def _handle_command(self, command: str):
        """Process user command and speak response"""
        if not command.strip():
            return
        if command.lower() in ["quit", "exit", "bye", "goodbye"]:
            self.speak("Goodbye! Have a great day.", async_mode=False)
            sys.exit(0)

        print(f"\n{CYAN}⏳ Chanakya is thinking...{RESET}")
        self.is_processing = True

        response = self.agent.process_input(command, voice_output=False)

        # Determine spoken part (first 2 sentences max for brevity)
        lines = [l.strip() for l in response.split('\n') if l.strip()]
        spoken = " ".join(lines[:2]) if lines else response
        # Cap to 200 chars for natural TTS
        if len(spoken) > 200:
            spoken = spoken[:200] + "."

        print(f"{CYAN}{BOLD}Chanakya:{RESET} {response}\n")
        self.speak(spoken, async_mode=False)
        self.is_processing = False


def run_siri_mode():
    """Entry point for Siri-style always-listening mode"""
    assistant = ChanakyaWakeAssistant()
    assistant.run()
