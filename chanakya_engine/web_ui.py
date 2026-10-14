import http.server
import socketserver
import json
import webbrowser
import threading
from .agent import ChanakyaAgent
from .config import CURRENT_OS

HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Chanakya — Personal AI Strategist & Desktop Assistant</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg: #090d16;
            --surface: rgba(22, 30, 46, 0.75);
            --border: rgba(255, 255, 255, 0.1);
            --primary: #f59e0b;
            --secondary: #fbbf24;
            --accent: #38bdf8;
            --text: #f8fafc;
            --text-dim: #94a3b8;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Outfit', sans-serif; }
        body {
            background: radial-gradient(circle at 50% 0%, #311c07 0%, var(--bg) 75%);
            color: var(--text);
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            padding: 20px 40px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border);
            backdrop-filter: blur(12px);
        }
        .brand {
            display: flex;
            align-items: center;
            gap: 12px;
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .badge {
            font-size: 11px;
            background: rgba(245, 158, 11, 0.15);
            color: var(--secondary);
            padding: 4px 10px;
            border-radius: 20px;
            border: 1px solid rgba(245, 158, 11, 0.3);
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        main {
            flex: 1;
            max-width: 1000px;
            width: 100%;
            margin: 0 auto;
            padding: 30px 20px;
            display: flex;
            flex-direction: column;
            gap: 24px;
        }
        .orb-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 25px 0 10px;
        }
        .orb {
            width: 125px;
            height: 125px;
            border-radius: 50%;
            background: radial-gradient(circle at 30% 30%, #fde68a, #f59e0b 60%, #b45309);
            box-shadow: 0 0 65px rgba(245, 158, 11, 0.6), inset 0 0 20px rgba(255, 255, 255, 0.6);
            animation: pulse 4s ease-in-out infinite alternate;
            position: relative;
        }
        .orb.active {
            animation: pulse 1.2s ease-in-out infinite alternate, glow 0.8s infinite alternate;
            background: radial-gradient(circle at 30% 30%, #fffbeb, #fbbf24 60%, #ea580c);
            box-shadow: 0 0 90px rgba(251, 191, 36, 0.95);
        }
        @keyframes pulse {
            0% { transform: scale(0.96); }
            100% { transform: scale(1.05); }
        }
        @keyframes glow {
            0% { filter: brightness(1); }
            100% { filter: brightness(1.35); }
        }
        .orb-status {
            margin-top: 15px;
            font-size: 14px;
            color: var(--text-dim);
            letter-spacing: 0.5px;
        }
        .chat-box {
            background: var(--surface);
            border: 1px solid var(--border);
            border-radius: 18px;
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            display: flex;
            flex-direction: column;
            gap: 14px;
            backdrop-filter: blur(16px);
        }
        .message {
            max-width: 80%;
            padding: 12px 18px;
            border-radius: 14px;
            line-height: 1.5;
            font-size: 15px;
            animation: fadeIn 0.3s ease;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user {
            align-self: flex-end;
            background: linear-gradient(135deg, #d97706, #f59e0b);
            color: white;
            border-bottom-right-radius: 4px;
        }
        .message.chanakya {
            align-self: flex-start;
            background: rgba(30, 41, 59, 0.85);
            border: 1px solid var(--border);
            border-bottom-left-radius: 4px;
        }
        .quick-actions {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            justify-content: center;
        }
        .action-chip {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border);
            padding: 8px 16px;
            border-radius: 30px;
            font-size: 13px;
            color: var(--text-dim);
            cursor: pointer;
            transition: all 0.2s;
        }
        .action-chip:hover {
            background: rgba(245, 158, 11, 0.15);
            color: var(--secondary);
            border-color: var(--secondary);
            transform: translateY(-2px);
        }
        .input-bar {
            display: flex;
            gap: 12px;
            background: var(--surface);
            border: 1px solid var(--border);
            padding: 8px 12px;
            border-radius: 16px;
            backdrop-filter: blur(16px);
        }
        .input-bar input {
            flex: 1;
            background: transparent;
            border: none;
            outline: none;
            color: var(--text);
            font-size: 16px;
            padding: 10px 14px;
        }
        .btn {
            background: linear-gradient(135deg, var(--secondary), var(--primary));
            border: none;
            color: #1a0f02;
            font-weight: 700;
            padding: 12px 22px;
            border-radius: 12px;
            cursor: pointer;
            transition: opacity 0.2s;
        }
        .btn:hover { opacity: 0.9; }
        .btn-mic {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text);
            padding: 12px 16px;
            border-radius: 12px;
            cursor: pointer;
            border: 1px solid var(--border);
            transition: all 0.2s;
        }
        .btn-mic.listening {
            background: #ef4444;
            color: white;
            animation: pulse 1s infinite alternate;
        }
    </style>
</head>
<body>
    <header>
        <div class="brand">
            <span>🏛️ Chanakya</span>
            <span class="badge">macOS & Windows</span>
        </div>
        <div style="font-size: 13px; color: var(--text-dim);">
            Created by: <strong>Ankush Choudhary</strong>
        </div>
    </header>

    <main>
        <div class="orb-container">
            <div class="orb" id="orb"></div>
            <div class="orb-status" id="orbStatus">Online & Ready</div>
        </div>

        <div class="quick-actions">
            <div class="action-chip" onclick="sendPrompt('Check battery status')">🔋 Battery Status</div>
            <div class="action-chip" onclick="sendPrompt('Play lo-fi beats on YouTube')">🎵 Play Lo-Fi YouTube</div>
            <div class="action-chip" onclick="sendPrompt('Search Google for AI trends')">🌐 AI News Search</div>
            <div class="action-chip" onclick="sendPrompt('Set volume to 50')">🔊 Volume 50%</div>
            <div class="action-chip" onclick="sendPrompt('Take a screenshot')">📸 Screenshot</div>
        </div>

        <div class="chat-box" id="chatBox">
            <div class="message chanakya">
                Namaste! I am Chanakya, your desktop AI strategist and personal assistant. Speak or type below to control your computer, search the web, play media, or save facts.
            </div>
        </div>

        <div class="input-bar">
            <button class="btn-mic" id="micBtn" onclick="toggleMic()" title="Voice Input">🎙️</button>
            <input type="text" id="userInput" placeholder="Ask Chanakya to do anything (e.g. 'Play music on YouTube', 'Open Chrome')..." onkeypress="handleKey(event)">
            <button class="btn" onclick="sendMessage()">Send</button>
        </div>
    </main>

    <script>
        const chatBox = document.getElementById('chatBox');
        const userInput = document.getElementById('userInput');
        const orb = document.getElementById('orb');
        const orbStatus = document.getElementById('orbStatus');
        const micBtn = document.getElementById('micBtn');

        function appendMessage(text, role) {
            const div = document.createElement('div');
            div.className = 'message ' + role;
            div.innerText = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }

        async function sendPrompt(text) {
            if (!text.trim()) return;
            appendMessage(text, 'user');
            orb.classList.add('active');
            orbStatus.innerText = 'Chanakya is executing...';

            try {
                const res = await fetch('/api/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: text })
                });
                const data = await res.json();
                orb.classList.remove('active');
                orbStatus.innerText = 'Online & Ready';
                appendMessage(data.response, 'chanakya');
            } catch (err) {
                orb.classList.remove('active');
                orbStatus.innerText = 'Error';
                appendMessage('Error communicating with Chanakya engine.', 'chanakya');
            }
        }

        function sendMessage() {
            const text = userInput.value;
            userInput.value = '';
            sendPrompt(text);
        }

        function handleKey(e) {
            if (e.key === 'Enter') sendMessage();
        }

        let recognition = null;
        let isListening = false;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRec();
            recognition.continuous = false;
            recognition.interimResults = false;

            recognition.onstart = () => {
                isListening = true;
                micBtn.classList.add('listening');
                orbStatus.innerText = 'Listening to voice...';
                orb.classList.add('active');
            };

            recognition.onresult = (e) => {
                const transcript = e.results[0][0].transcript;
                userInput.value = transcript;
                sendMessage();
            };

            recognition.onend = () => {
                isListening = false;
                micBtn.classList.remove('listening');
                orb.classList.remove('active');
                orbStatus.innerText = 'Online & Ready';
            };
        }

        function toggleMic() {
            if (!recognition) {
                alert('Web Speech API is not supported in this browser. Please type your message.');
                return;
            }
            if (isListening) {
                recognition.stop();
            } else {
                recognition.start();
            }
        }
    </script>
</body>
</html>
"""

class WebHandler(http.server.BaseHTTPRequestHandler):
    agent: ChanakyaAgent = None

    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))
        elif self.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            status = {
                "assistant": "Chanakya",
                "os": CURRENT_OS,
                "author": "Ankush Choudhary",
                "llm_connected": self.agent.llm.is_connected,
                "model": self.agent.llm.model
            }
            self.wfile.write(json.dumps(status).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/chat":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)
            user_msg = data.get("message", "")
            
            response = self.agent.process_input(user_msg, voice_output=True)
            
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"response": response}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

def run_web_dashboard(port: int = 7860):
    agent = ChanakyaAgent()
    WebHandler.agent = agent

    server_address = ("", port)
    httpd = socketserver.TCPServer(server_address, WebHandler)
    url = f"http://localhost:{port}"
    print(f"\n🌐 Chanakya Web Dashboard running at: {url}")
    print("Press Ctrl+C to stop.\n")
    webbrowser.open(url)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down web server...")
        httpd.server_close()
