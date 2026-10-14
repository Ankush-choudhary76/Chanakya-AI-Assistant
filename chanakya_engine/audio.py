import subprocess
import threading
import sys
import os
from .config import IS_MAC, IS_WINDOWS

class TextToSpeech:
    """Cross-platform Text-To-Speech engine (Native Mac 'say', Windows SAPI/pyttsx3)"""
    def __init__(self):
        self.engine = None
        if not IS_MAC:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
            except Exception:
                self.engine = None

    def speak(self, text: str, async_mode: bool = True):
        if not text or not text.strip():
            return

        def _run_tts():
            clean_text = text.replace('"', '\\"').replace("'", "\\'")
            # Mac has native ultra-fast 'say' command with zero setup
            if IS_MAC:
                try:
                    subprocess.run(["say", "-r", "185", clean_text], check=True)
                    return
                except Exception:
                    pass

            # Windows native SAPI through powershell fallback
            if IS_WINDOWS:
                try:
                    ps_cmd = f'Add-Type -AssemblyName System.Speech; $speak = New-Object System.Speech.Synthesis.SpeechSynthesizer; $speak.Speak("{clean_text}");'
                    subprocess.run(["powershell", "-Command", ps_cmd], check=True)
                    return
                except Exception:
                    pass

            # Fallback to pyttsx3 if initialized
            if self.engine:
                try:
                    self.engine.say(text)
                    self.engine.runAndWait()
                except Exception:
                    pass

        if async_mode:
            thread = threading.Thread(target=_run_tts, daemon=True)
            thread.start()
        else:
            _run_tts()

class SpeechToText:
    """Speech to text engine using SpeechRecognition or Whisper with terminal fallback"""
    def __init__(self):
        self.recognizer = None
        self.mic = None
        try:
            import speech_recognition as sr
            self.recognizer = sr.Recognizer()
            self.mic = sr.Microphone()
            # Adjust ambient noise
            with self.mic as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
        except Exception:
            self.recognizer = None

    def listen(self, timeout: int = 5) -> str:
        if not self.recognizer or not self.mic:
            return ""

        import speech_recognition as sr
        try:
            with self.mic as source:
                print("🎙️ Listening... (Speak now)")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=10)
                print("⏳ Transcribing audio...")
                text = self.recognizer.recognize_google(audio)
                return text.strip()
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[Audio Error] {e}")
            return ""
