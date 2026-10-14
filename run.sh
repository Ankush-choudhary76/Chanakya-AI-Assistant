#!/usr/bin/env bash
# One-click launcher for macOS & Linux
# Usage: ./run.sh           → CLI mode
#        ./run.sh --siri    → Siri-style always-listening voice mode
#        ./run.sh --web     → Web Dashboard (browser)

echo "🏛️ Starting Chanakya AI Assistant..."

# Check Python3
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3."
    exit 1
fi

# Run Chanakya
python3 main.py "$@"
