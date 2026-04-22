import speech_recognition as sr
try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
import sys
import datetime
import re
import webbrowser
import wikipedia
import os
import subprocess
import platform
import json
import requests
import threading
import time
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
import math

# Set appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AdvancedAssistant:
    def __init__(self, gui):
        self.gui = gui
        if pyttsx3:
            self.engine = pyttsx3.init()
        else:
            self.engine = None
        self.recognizer = sr.Recognizer()
        self.commands_file = "commands.json"
        self.context = {"last_query": None, "last_response": None}
        self.is_listening = False
        self.wake_word = "hey assistant"
        self.weather_api_key = "YOUR_OPENWEATHERMAP_KEY" # Placeholder
        self.news_api_key = "YOUR_NEWSAPI_KEY" # Placeholder
        
        # Load custom commands
        self.custom_commands = self.load_custom_commands()

    def load_custom_commands(self):
        if os.path.exists(self.commands_file):
            try:
                with open(self.commands_file, 'r') as f:
                    return json.load(f).get("custom_commands", [])
            except: return []
        return []

    def speak(self, text):
        self.gui.update_status(f"Speaking...")
        self.gui.add_to_history("Assistant", text)
        print(f"Assistant: {text}")
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()
        self.gui.update_status("Idle")

    def get_weather(self, city="London"):
        """Fetch weather data (Mocked if no key)"""
        if self.weather_api_key == "YOUR_OPENWEATHERMAP_KEY":
            return "I don't have a weather API key configured, but it's probably sunny somewhere!"
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            res = requests.get(url).json()
            temp = res['main']['temp']
            desc = res['weather'][0]['description']
            return f"The current temperature in {city} is {temp}°C with {desc}."
        except:
            return "I couldn't fetch the weather right now."

    def get_news(self):
        """Fetch top headlines (Mocked if no key)"""
        if self.news_api_key == "YOUR_NEWSAPI_KEY":
            return "I can't fetch the news without an API key, but the world keeps turning!"
        try:
            url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={self.news_api_key}"
            res = requests.get(url).json()
            articles = res['articles'][:3]
            headlines = [a['title'] for a in articles]
            return "Here are the top headlines: " + ". ".join(headlines)
        except:
            return "I'm having trouble accessing the news right now."

    def handle_math(self, command):
        operators = {'plus': '+', 'minus': '-', 'times': '*', 'divided by': '/'}
        pattern = r'(\d+)\s*(plus|minus|times|multiplied by|divided by|over|\+|\-|\*|\/)\s*(\d+)'
        match = re.search(pattern, command)
        if match:
            n1, op_word, n2 = float(match.group(1)), match.group(2), float(match.group(3))
            op = operators.get(op_word, op_word)
            try:
                if op == '+': res = n1 + n2
                elif op == '-': res = n1 - n2
                elif op == '*': res = n1 * n2
                elif op == '/': res = n1 / n2 if n2 != 0 else "Error"
                if isinstance(res, float) and res.is_integer(): res = int(res)
                return f"The answer is {res}"
            except: return "Math error."
        return None

    def process_command(self, command):
        if not command: return
        
        self.gui.add_to_history("User", command)
        cmd = command.lower()

        # Greetings & Context
        if any(g in cmd for g in ["hello", "hi"]):
            self.speak("Hello! I'm listening. How can I help?")
        
        elif "thank you" in cmd:
            self.speak("You're very welcome!")

        # Weather & News
        elif "weather" in cmd:
            city_match = re.search(r'weather in ([\w\s]+)', cmd)
            city = city_match.group(1) if city_match else "your city"
            self.speak(self.get_weather(city))

        elif "news" in cmd:
            self.speak(self.get_news())

        # Time/Date
        elif "time" in cmd:
            self.speak(f"The time is {datetime.datetime.now().strftime('%I:%M %p')}")
        
        elif "date" in cmd:
            self.speak(f"Today is {datetime.datetime.now().strftime('%B %d, %Y')}")

        # Web Search & Wikipedia
        elif "search for" in cmd:
            q = cmd.replace("search for", "").strip()
            webbrowser.open(f"https://www.google.com/search?q={q}")
            self.speak(f"Searching for {q}")

        elif "tell me about" in cmd:
            topic = cmd.replace("tell me about", "").strip()
            try:
                summary = wikipedia.summary(topic, sentences=2)
                self.speak(summary)
            except: self.speak("I couldn't find that on Wikipedia.")

        # Math
        elif any(o in cmd for o in ["plus", "minus", "times", "divided"]):
            res = self.handle_math(cmd)
            if res: self.speak(res)

        # System Controls
        elif "open" in cmd:
            app = cmd.replace("open", "").strip()
            if "notepad" in app: subprocess.Popen(["notepad.exe"])
            elif "chrome" in app: subprocess.Popen(["start", "chrome"], shell=True)
            self.speak(f"Opening {app}")

        # Exit
        elif any(e in cmd for e in ["exit", "quit", "goodbye"]):
            self.speak("Goodbye! Closing assistant.")
            self.gui.root.quit()

        else:
            # Check Custom Commands
            for custom in self.custom_commands:
                if custom["trigger"] in cmd:
                    if custom["action_type"] == "url": webbrowser.open(custom["action"])
                    self.speak(f"Running custom command: {custom['trigger']}")
                    return
            
            self.speak(f"I heard {cmd}, but I'm not sure how to help with that yet.")

        self.context["last_query"] = cmd

class AssistantGUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Premium Voice Assistant")
        self.root.geometry("600x700")
        
        self.setup_ui()
        self.backend = AdvancedAssistant(self)
        
        self.anim_running = True
        self.wave_offset = 0
        self.update_wave()
        
        # Start listening thread
        self.listen_thread = threading.Thread(target=self.continuous_listening, daemon=True)
        self.listen_thread.start()

    def setup_ui(self):
        # Header
        self.label = ctk.CTkLabel(self.root, text="Voice Assistant", font=("Outfit", 28, "bold"))
        self.label.pack(pady=20)

        # Wave Animation Canvas
        self.canvas = tk.Canvas(self.root, width=500, height=150, bg="#1a1a1a", highlightthickness=0)
        self.canvas.pack(pady=10)

        # Status Label
        self.status_label = ctk.CTkLabel(self.root, text="Waiting for 'Hey Assistant'...", font=("Inter", 14), text_color="#aaaaaa")
        self.status_label.pack(pady=5)

        # History Textbox
        self.history_box = ctk.CTkTextbox(self.root, width=500, height=300, font=("Inter", 12))
        self.history_box.pack(pady=20, padx=20)
        self.history_box.insert("0.0", "--- Command History ---\n\n")
        self.history_box.configure(state="disabled")

        # Controls
        self.btn = ctk.CTkButton(self.root, text="Manual Trigger", command=self.manual_trigger)
        self.btn.pack(pady=10)

    def update_status(self, text):
        self.status_label.configure(text=text)

    def add_to_history(self, sender, text):
        self.history_box.configure(state="normal")
        self.history_box.insert("end", f"{sender}: {text}\n\n")
        self.history_box.see("end")
        self.history_box.configure(state="disabled")

    def update_wave(self):
        if not self.anim_running: return
        self.canvas.delete("all")
        width = 500
        height = 150
        points = []
        
        # Determine amplitude based on state
        amplitude = 40 if "Listening" in self.status_label.cget("text") else 10
        if "Speaking" in self.status_label.cget("text"): amplitude = 60
        
        for x in range(0, width, 5):
            y = (height/2) + amplitude * math.sin((x + self.wave_offset) * 0.05)
            points.append(x)
            points.append(y)
            
        self.canvas.create_line(points, fill="#3b8ed0", width=3, smooth=True)
        self.wave_offset += 5
        self.root.after(50, self.update_wave)

    def manual_trigger(self):
        threading.Thread(target=self.listen_and_process, daemon=True).start()

    def listen_and_process(self):
        self.update_status("Listening...")
        recognizer = self.backend.recognizer
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
                self.update_status("Processing...")
                command = recognizer.recognize_google(audio)
                self.backend.process_command(command)
            except:
                self.update_status("Idle")

    def continuous_listening(self):
        recognizer = self.backend.recognizer
        while True:
            try:
                with sr.Microphone() as source:
                    recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    audio = recognizer.listen(source, phrase_time_limit=3)
                    text = recognizer.recognize_google(audio).lower()
                    
                    if self.backend.wake_word in text:
                        self.backend.speak("Yes, I'm here. How can I help?")
                        self.listen_and_process()
            except:
                pass
            time.sleep(0.1)

if __name__ == "__main__":
    app = AssistantGUI()
    app.root.mainloop()
