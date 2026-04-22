from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import threading
import os
import json
from assistant_gui import AdvancedAssistant # Import the logic from our previous script

app = Flask(__name__)
CORS(app)

# Mock a GUI object since the backend expects one to update status/history
class MockGUI:
    def update_status(self, text): print(f"Status: {text}")
    def add_to_history(self, sender, text): 
        if not hasattr(self, 'history'): self.history = []
        self.history.append({"sender": sender, "text": text})
    def root_quit(self): pass

mock_gui = MockGUI()
assistant = AdvancedAssistant(mock_gui)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/command', methods=['POST'])
def process_command():
    data = request.json
    command = data.get('command')
    if command:
        # Run in a thread so it doesn't block Flask if it speaks
        threading.Thread(target=assistant.process_command, args=(command,)).start()
        return jsonify({"status": "success", "message": f"Processing: {command}"})
    return jsonify({"status": "error", "message": "No command received"})

@app.route('/history', methods=['GET'])
def get_history():
    return jsonify(getattr(mock_gui, 'history', []))

@app.route('/listen', methods=['GET'])
def listen():
    # This triggers the server-side microphone
    def run_listen():
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                text = recognizer.recognize_google(audio)
                assistant.process_command(text)
            except:
                pass
    
    threading.Thread(target=run_listen).start()
    return jsonify({"status": "listening started"})

if __name__ == '__main__':
    # Create templates folder if it doesn't exist
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    app.run(debug=True, port=5000)
