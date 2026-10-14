#!/usr/bin/env python3
"""
Chanakya — Personal AI Strategist & Desktop Assistant (macOS & Windows Cross-Platform Engine)
Created & Maintained by Ankush Choudhary (https://github.com/Ankush-choudhary76)

Usage:
  python3 main.py            → Terminal CLI Mode
  python3 main.py --web      → Futuristic Web Dashboard (browser)
  python3 main.py --siri     → Siri-style Always-Listening Voice Mode 🎙️
"""

import sys
import argparse

def main():
    parser = argparse.ArgumentParser(
        description="Chanakya Personal AI Assistant — Cross-Platform Agent (macOS & Windows)"
    )
    parser.add_argument(
        "--web",
        action="store_true",
        help="Launch the Chanakya Web Dashboard UI in your browser"
    )
    parser.add_argument(
        "--siri",
        action="store_true",
        help="🎙️ Siri-style always-listening voice mode (say 'Chanakya' to activate)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port for the web dashboard (default: 7860)"
    )

    args = parser.parse_args()

    if args.web:
        from chanakya_engine.web_ui import run_web_dashboard
        run_web_dashboard(port=args.port)
    elif args.siri:
        from chanakya_engine.wake import run_siri_mode
        run_siri_mode()
    else:
        from chanakya_engine.cli import run_cli
        run_cli()

if __name__ == "__main__":
    main()
