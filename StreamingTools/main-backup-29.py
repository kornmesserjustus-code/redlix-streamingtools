from flask import Flask, jsonify, request, render_template_string
from threading import Lock
import time

app = Flask(__name__)
lock = Lock()

# Global state with default values
state = {
    "timer": {
        "value": 0.0,
        "running": False,
        "visible": True,
        "last_update": time.time()
    },
    "countdown": {
        "value": 0.0,
        "initial": 0.0,  # Add initial value tracking
        "running": False,
        "visible": True,
        "last_update": time.time()
    },
    "message": {
        "text": "",
        "color": "#b71c1c",
        "expires_at": 0.0
    }
}

CONTROL_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Stream Control Panel</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #6366f1;
            --primary-hover: #4f46e5;
            --bg: #0f172a;
            --surface: #1e293b;
            --surface-hover: #2c3b52;
            --text: #e2e8f0;
            --text-secondary: #94a3b8;
            --danger: #dc2626;
            --success: #16a34a;
            --border: #334155;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: var(--bg);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            min-height: 100vh;
            padding: 2rem;
            line-height: 1.5;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
        }

        .panel {
            background: var(--surface);
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            border: 1px solid var(--border);
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            transition: transform 0.2s;
        }

        .panel:hover {
            transform: translateY(-2px);
        }

        h2 {
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 1.25rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        h2::before {
            content: '';
            display: block;
            width: 4px;
            height: 1.25rem;
            background: var(--primary);
            border-radius: 2px;
        }

        .controls {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            align-items: center;
        }

        button {
            background: var(--surface-hover);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.6rem 1.2rem;
            border-radius: 8px;
            cursor: pointer;
            font-weight: 500;
            font-size: 0.875rem;
            transition: all 0.2s;
            min-width: 90px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 0.5rem;
        }

        button:hover {
            background: var(--primary);
            border-color: var(--primary);
            transform: translateY(-1px);
        }

        .toggle {
            background: var(--danger);
            border-color: var(--danger);
        }

        .toggle.active {
            background: var(--success);
            border-color: var(--success);
        }

        input, select {
            background: var(--surface);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 0.6rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            transition: all 0.2s;
        }

        input:focus, select:focus {
            outline: none;
            border-color: var(--primary);
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
        }

        .time-input-group {
            display: flex;
            gap: 0.5rem;
            align-items: center;
            background: var(--surface-hover);
            padding: 0.75rem;
            border-radius: 8px;
            border: 1px solid var(--border);
        }

        .time-input-wrapper {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 0.25rem;
        }

        .time-input-wrapper label {
            font-size: 0.75rem;
            color: var(--text-secondary);
            font-weight: 500;
        }

        .time-separator {
            color: var(--text-secondary);
            font-weight: 600;
            margin: 0 0.25rem;
            padding-top: 0.5rem;
        }

        .status {
            font-family: 'Inter', monospace;
            margin-top: 1rem;
            color: var(--text-secondary);
            font-size: 1.25rem;
            font-weight: 500;
            background: var(--surface-hover);
            padding: 0.75rem;
            border-radius: 8px;
            text-align: center;
            border: 1px solid var(--border);
        }

        .message-controls {
            display: grid;
            grid-template-columns: auto 1fr auto auto;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }

        input[type="color"] {
            padding: 0.25rem;
            width: 80px;
            height: 40px;
            cursor: pointer;
        }

        .start {
            background: var(--primary);
            border-color: var(--primary);
        }

        .start:hover {
            background: var(--primary-hover);
            border-color: var(--primary-hover);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="panel">
            <h2>Timer</h2>
            <div class="controls">
                <button onclick="timerControl('start')" class="start">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    Start
                </button>
                <button onclick="timerControl('stop')">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 10a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z"/></svg>
                    Stop
                </button>
                <button onclick="timerControl('reset')">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"/></svg>
                    Reset
                </button>
                <button class="toggle" id="timerVisibility" onclick="toggleVisibility('timer')">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/></svg>
                    Toggle
                </button>
            </div>
            <div class="status" id="timerStatus">00:00:00</div>
        </div>

        <div class="panel">
            <h2>Countdown</h2>
            <div class="controls">
                <div class="time-input-group">
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownHours" placeholder="00" min="0" max="23" value="0" style="width: 70px">
                        <label>Hours</label>
                    </div>
                    <span class="time-separator">:</span>
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownMinutes" placeholder="00" min="0" max="59" value="5" style="width: 70px">
                        <label>Minutes</label>
                    </div>
                    <span class="time-separator">:</span>
                    <div class="time-input-wrapper">
                        <input type="number" id="countdownSeconds" placeholder="00" min="0" max="59" value="0" style="width: 70px">
                        <label>Seconds</label>
                    </div>
                </div>
                <button onclick="startCountdown()" class="start">
                    <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>
                    Start
                </button>
                <button onclick="countdownControl('stop')">Stop</button>
                <button onclick="countdownControl('reset')">Reset</button>
                <button class="toggle" id="countdownVisibility" onclick="toggleVisibility('countdown')">Toggle</button>
            </div>
            <div class="status" id="countdownStatus">00:00:00</div>
        </div>

        <div class="panel">
            <h2>Message</h2>
            <div class="message-controls">
                <select id="messageEmoji">
                    <option value="">No Emoji</option>
                    <option value="⚠️">⚠️ Warning</option>
                    <option value="🔴">🔴 Alert</option>
                    <option value="📢">📢 Announce</option>
                    <option value="💡">💡 Info</option>
                    <option value="🎮">🎮 Game</option>
                    <option value="⭐">⭐ Star</option>
                </select>
                <input type="text" id="messageText" placeholder="Enter your message here...">
                <select id="messageDuration">
                    <option value="3">3 seconds</option>
                    <option value="5" selected>5 seconds</option>
                    <option value="10">10 seconds</option>
                    <option value="15">15 seconds</option>
                    <option value="30">30 seconds</option>
                    <option value="60">1 minute</option>
                </select>
                <input type="color" id="messageColor" value="#b71c1c">
            </div>
            <div class="controls">
                <button onclick="sendMessage()" class="start">Show Message</button>
                <button onclick="clearMessage()">Clear</button>
            </div>
        </div>
    </div>

    <script>
        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }

        async function updateState() {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                
                // Update displays
                document.getElementById('timerStatus').textContent = formatTime(data.timer.value);
                document.getElementById('countdownStatus').textContent = formatTime(data.countdown.value);
                
                // Update visibility buttons
                document.getElementById('timerVisibility').classList.toggle('active', data.timer.visible);
                document.getElementById('countdownVisibility').classList.toggle('active', data.countdown.visible);
            } catch (err) {
                console.error('Failed to update state:', err);
            }
            setTimeout(updateState, 100);
        }

        async function apiCall(endpoint, method='POST', data={}) {
            try {
                const response = await fetch(`/api/${endpoint}`, {
                    method,
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(data)
                });
                return await response.json();
            } catch (err) {
                console.error('API call failed:', err);
                return null;
            }
        }

        function timerControl(action) {
            apiCall(`timer/${action}`);
        }

        function countdownControl(action) {
            apiCall(`countdown/${action}`);
        }

        function startCountdown() {
            const hours = parseInt(document.getElementById('countdownHours').value) || 0;
            const minutes = parseInt(document.getElementById('countdownMinutes').value) || 0;
            const seconds = parseInt(document.getElementById('countdownSeconds').value) || 0;
            const totalMinutes = (hours * 60) + minutes + (seconds / 60);
            apiCall('countdown/start', 'POST', {minutes: totalMinutes});
        }

        function toggleVisibility(element) {
            apiCall(`visibility/${element}`);
        }

        function sendMessage() {
            const text = document.getElementById('messageText').value;
            const emoji = document.getElementById('messageEmoji').value;
            const color = document.getElementById('messageColor').value;
            const duration = document.getElementById('messageDuration').value;
            const fullText = emoji ? `${emoji} ${text} ${emoji}` : text;
            apiCall('message', 'POST', {text: fullText, color, duration});
        }

        function clearMessage() {
            apiCall('message/clear');
        }

        window.onload = updateState;

        function updateTimerBlinkMode(mode) {
            const timerBar = document.querySelector('#timer .progress-bar-fill');
            timerBar.classList.remove('blink-fast', 'blink-slow');
            if (mode === 'seconds') {
                timerBar.classList.add('blink-fast');
            } else if (mode === 'minutes') {
                timerBar.classList.add('blink-slow');
            }
        }
    </script>
</body>
</html>
"""

DISPLAY_HTML = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Stream Display</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=JetBrains+Mono:wght@700&display=swap" rel="stylesheet">
    <style>
        body {
            margin: 0;
            padding: 30px;
            background: #00FF00;
            color: white;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            height: 100vh;
        }
        .display-container {
            position: fixed;
            top: 30px;
            left: 30px;
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        .display-box {
            background: linear-gradient(110deg, rgba(0,0,0,0.95), rgba(0,0,0,0.85));
            padding: 15px 25px 20px 25px;  // Added padding at bottom for progress bar
            border-radius: 16px;
            display: none;
            position: relative;
            overflow: hidden;
            min-width: 280px;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .display-box::before {
            content: '';
            position: absolute;
            inset: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: translateX(-100%);
            animation: shimmer 10s infinite;
        }
        @keyframes shimmer {
            100% { transform: translateX(100%); }
        }
        .display-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 2px;
            opacity: 0.5;
            margin-bottom: 8px;
            font-weight: 600;
            position: relative;
            padding-left: 12px;
        }
        .display-label::before {
            content: '';
            position: absolute;
            left: 0;
            top: 50%;
            width: 6px;
            height: 6px;
            background: currentColor;
            border-radius: 50%;
            transform: translateY(-50%);
        }
        .time-display {
            font-family: 'JetBrains Mono', monospace;
            font-size: 42px;
            font-weight: 700;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            margin-bottom: 12px;  // Add space for progress bar
        }
        .time-group {
            background: rgba(0,0,0,0.5);
            padding: 8px 12px;
            border-radius: 8px;
            position: relative;
            min-width: 60px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.15);
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            color: #fff;  // Direct white color for better visibility
        }
        .time-group::after {
            content: attr(data-label);
            position: absolute;
            bottom: -16px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 10px;
            color: rgba(255,255,255,0.4);
            font-family: 'Inter', sans-serif;
            letter-spacing: 1px;
        }
        .time-separator {
            color: rgba(255,255,255,0.5);  // Make separators visible
            margin: 0 2px;
            animation: blink 10s infinite;
        }
        @keyframes blink {
            0%, 98% { opacity: 0.5; }
            99% { opacity: 0.2; }
        }
        .message {
            background: linear-gradient(110deg, rgba(0,0,0,0.95), rgba(0,0,0,0.85));
            padding: 25px 40px;
            border-radius: 16px;
            font-family: 'Inter', sans-serif;
            font-size: 42px;
            font-weight: 600;
            text-align: center;
            display: none;
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            box-shadow: 
                0 10px 30px rgba(0,0,0,0.3),
                inset 0 1px 0 rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.1);
            max-width: 80vw;
            backdrop-filter: blur(10px);
            animation: messageIn 0.3s cubic-bezier(0.2, 0.9, 0.3, 1.1);
        }
        .message::before {
            content: '';
            position: absolute;
            inset: 0;
            background: var(--msg-color, #b71c1c);
            opacity: 0.8;
            border-radius: inherit;
            z-index: -1;
        }
        .message-progress {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 0 0 16px 16px;
            overflow: hidden;
        }
        .message-progress-bar {
            height: 100%;
            width: 100%;
            background: rgba(255,255,255,0.3);
            transform-origin: left;
            animation: progress var(--duration, 5s) linear forwards;
        }
        @keyframes progress {
            to { transform: scaleX(0); }
        }
        .progress-bar {
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 8px;
            background: rgba(0,0,0,0.3);
            border-radius: 0 0 16px 16px;
            overflow: hidden;
            opacity: 0;  /* Hidden by default */
            transition: opacity 0.3s ease;  /* Smooth transition */
        }
        .progress-bar.active {
            opacity: 1;  /* Show when active */
        }
        .progress-bar-fill {
            height: 100%;
            width: 100%;
            background: rgba(255,255,255,0.2);
            transition: width 0.3s linear;
        }
        #timer .progress-bar-fill {
            background: #4CAF50;
            width: 100% !important;  # Ensure full width
        }
        #timer .progress-bar-fill.blink-fast {
            animation: blinkFast 0.5s infinite;
        }
        #timer .progress-bar-fill.blink-slow {
            animation: blinkSlow 3s infinite;
        }
        @keyframes blinkFast {
            50% { opacity: 0.3; }
        }
        @keyframes blinkSlow {
            50% { opacity: 0.3; }
        }
        #countdown .progress-bar-fill {
            background: linear-gradient(90deg, #FF5722, #FF8A65);
        }
    </style>
</head>
<body>
    <div class="display-container">
        <div id="timer" class="display-box">
            <div class="display-label">Timer</div>
            <div class="time-display">
                <span class="time-group" data-label="HRS">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="MIN">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="SEC">00</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill"></div>
            </div>
        </div>
        <div id="countdown" class="display-box">
            <div class="display-label">Countdown</div>
            <div class="time-display">
                <span class="time-group" data-label="HRS">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="MIN">00</span>
                <span class="time-separator">:</span>
                <span class="time-group" data-label="SEC">00</span>
            </div>
            <div class="progress-bar">
                <div class="progress-bar-fill"></div>
            </div>
        </div>
    </div>
    <div id="message" class="message"></div>

    <script>
        function updateTimeDisplay(element, timeStr) {
            const [h, m, s] = timeStr.split(':');
            const groups = element.querySelectorAll('.time-group');
            groups[0].textContent = h;
            groups[1].textContent = m;
            groups[2].textContent = s;
        }

        async function updateDisplay() {
            try {
                const response = await fetch('/api/state');
                const data = await response.json();
                
                // Update timer
                const timerElement = document.getElementById('timer');
                timerElement.style.display = data.timer.visible ? 'block' : 'none';
                updateTimeDisplay(timerElement, formatTime(data.timer.value));
                
                // Update timer progress bar
                const timerProgressBar = timerElement.querySelector('.progress-bar');
                timerProgressBar.classList.toggle('active', data.timer.running);
                timerProgressBar.querySelector('.progress-bar-fill').style.width = '100%';

                // Update countdown
                const countdownElement = document.getElementById('countdown');
                countdownElement.style.display = data.countdown.visible ? 'block' : 'none';
                updateTimeDisplay(countdownElement, formatTime(data.countdown.value));

                // Update countdown progress and ensure progress bar is visible when running
                const countdownProgressBar = countdownElement.querySelector('.progress-bar');
                countdownProgressBar.classList.toggle('active', data.countdown.running);
                if (data.countdown.running && data.countdown.initial > 0) {
                    const progress = (data.countdown.value / data.countdown.initial) * 100;
                    countdownProgressBar.querySelector('.progress-bar-fill').style.width = `${progress}%`;
                } else {
                    countdownProgressBar.querySelector('.progress-bar-fill').style.width = '0%';
                }
                
                // Update message
                const messageElement = document.getElementById('message');
                if (data.message.text && Date.now() / 1000 < data.message.expires_at) {
                    if (messageElement.style.display !== 'block') {
                        messageElement.style.display = 'block';
                        messageElement.style.setProperty('--msg-color', data.message.color);
                        messageElement.innerHTML = `
                            ${data.message.text}
                            <div class="message-progress">
                                <div class="message-progress-bar"></div>
                            </div>
                        `;
                        const duration = Math.max(0, data.message.expires_at - Date.now() / 1000);
                        messageElement.style.setProperty('--duration', `${duration}s`);
                    }
                } else {
                    messageElement.style.display = 'none';
                }
            } catch (err) {
                console.error('Failed to update display:', err);
            }
            setTimeout(updateDisplay, 100);
        }

        function formatTime(seconds) {
            const h = Math.floor(seconds / 3600);
            const m = Math.floor((seconds % 3600) / 60);
            const s = Math.floor(seconds % 60);
            return `${h.toString().padStart(2,'0')}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
        }

        window.onload = updateDisplay;
    </script>
</body>
</html>
"""

# Routes
@app.route('/')
def control_panel():
    return render_template_string(CONTROL_HTML)

@app.route('/display')
def display():
    return render_template_string(DISPLAY_HTML)

@app.route('/api/state')
def get_state():
    with lock:
        current_time = time.time()
        
        # Update timer if running
        if state['timer']['running']:
            elapsed = current_time - state['timer']['last_update']
            state['timer']['value'] += elapsed
            state['timer']['last_update'] = current_time
        
        # Update countdown if running
        if state['countdown']['running']:
            elapsed = current_time - state['countdown']['last_update']
            state['countdown']['value'] = max(0, state['countdown']['value'] - elapsed)
            state['countdown']['last_update'] = current_time
            if state['countdown']['value'] <= 0:
                state['countdown']['running'] = False
        
        return jsonify(state)

# Timer endpoints
@app.route('/api/timer/<action>', methods=['POST'])
def timer_control(action):
    with lock:
        if action == 'start':
            state['timer']['running'] = True
            state['timer']['last_update'] = time.time()
        elif action == 'stop':
            state['timer']['running'] = False
        elif action == 'reset':
            state['timer']['value'] = 0
            state['timer']['running'] = False
    return jsonify({'success': True})

# Countdown endpoints
@app.route('/api/countdown/<action>', methods=['POST'])
def countdown_control(action):
    with lock:
        if action == 'start':
            data = request.get_json()
            minutes = float(data.get('minutes', 0))
            total_seconds = minutes * 60
            state['countdown']['value'] = total_seconds
            state['countdown']['initial'] = total_seconds  # Store initial value
            state['countdown']['running'] = True
            state['countdown']['last_update'] = time.time()
        elif action == 'stop':
            state['countdown']['running'] = False
        elif action == 'reset':
            state['countdown']['value'] = 0
            state['countdown']['initial'] = 0
            state['countdown']['running'] = False
    return jsonify({'success': True})

# Visibility toggle endpoints
@app.route('/api/visibility/<element>', methods=['POST'])
def toggle_visibility(element):
    with lock:
        if element in ['timer', 'countdown']:
            state[element]['visible'] = not state[element]['visible']
    return jsonify({'success': True})

# Message endpoints
@app.route('/api/message', methods=['POST'])
def set_message():
    with lock:
        data = request.get_json()
        state['message']['text'] = data.get('text', '')
        state['message']['color'] = data.get('color', '#b71c1c')
        duration = float(data.get('duration', 5))
        state['message']['expires_at'] = time.time() + duration
    return jsonify({'success': True})

@app.route('/api/message/clear', methods=['POST'])
def clear_message():
    with lock:
        state['message']['text'] = ''
        state['message']['expires_at'] = 0
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8765, debug=True)