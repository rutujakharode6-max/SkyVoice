import speech_recognition as sr
import pyttsx3
import sys
import datetime
import re
import webbrowser
import wikipedia
import os
import subprocess
import platform
import json

# Initialize the text-to-speech engine
engine = pyttsx3.init()
COMMANDS_FILE = "commands.json"

def load_custom_commands():
    if os.path.exists(COMMANDS_FILE):
        try:
            with open(COMMANDS_FILE, 'r') as f:
                return json.load(f).get("custom_commands", [])
        except Exception:
            return []
    return []

def save_custom_command(trigger, action_type, action):
    commands = load_custom_commands()
    commands.append({
        "trigger": trigger,
        "action_type": action_type,
        "action": action
    })
    with open(COMMANDS_FILE, 'w') as f:
        json.dump({"custom_commands": commands}, f, indent=2)

def speak(text):
    """Function to make the assistant speak"""
    print(f"Assistant: {text}")
    engine.say(text)
    engine.runAndWait()

def listen():
    """Function to listen for user commands"""
    recognizer = sr.Recognizer()
    
    try:
        with sr.Microphone() as source:
            print("\nListening...")
            # Adjust for ambient noise for better accuracy
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            
        print("Recognizing...")
        command = recognizer.recognize_google(audio).lower()
        print(f"User: {command}")
        return command
        
    except sr.RequestError:
        speak("I'm sorry, my speech service is down.")
    except sr.UnknownValueError:
        speak("I didn't quite catch that. Could you repeat?")
    except (sr.WaitTimeoutError, Exception) as e:
        if "Could not find PyAudio" in str(e) or "no microphone" in str(e).lower():
            speak("I couldn't find a microphone. Please check your connection.")
        else:
            print(f"Error: {e}")
            
    return None

def handle_math(command):
    """Parses and solves basic math problems from voice commands"""
    # Define mapping for word-based operators
    operators = {
        'plus': '+',
        'minus': '-',
        'times': '*',
        'multiplied by': '*',
        'divided by': '/',
        'over': '/'
    }
    
    # regex to find numbers and operators
    # Matches: [number] [operator words/symbols] [number]
    pattern = r'(\d+)\s*(plus|minus|times|multiplied by|divided by|over|\+|\-|\*|\/)\s*(\d+)'
    match = re.search(pattern, command)
    
    if match:
        num1 = float(match.group(1))
        op_word = match.group(2)
        num2 = float(match.group(3))
        
        op = operators.get(op_word, op_word)
        
        try:
            if op == '+': result = num1 + num2
            elif op == '-': result = num1 - num2
            elif op == '*': result = num1 * num2
            elif op == '/': 
                if num2 == 0: return "I can't divide by zero."
                result = num1 / num2
            
            # Format result to remove .0 if it's an integer
            if result.is_integer():
                result = int(result)
            
            return f"The answer is {result}"
        except Exception:
            return "I had trouble calculating that."
    
    return None

def process_command(command):
    """Function to handle recognized commands"""
    if command is None:
        return True

    # Greeting responses
    greetings = ["hello", "hi", "good morning", "hey"]
    
    if any(greet in command for greet in greetings):
        if "good morning" in command:
            speak("Good morning! How can I help you today?")
        else:
            speak("Hello! I am your Python voice assistant. How can I assist you?")
    
    # Time and Date queries
    elif "time" in command:
        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M %p")
        speak(f"The current time is {current_time}")
        
    elif "date" in command or "today" in command:
        now = datetime.datetime.now()
        current_date = now.strftime("%B %d, %Y")
        speak(f"Today's date is {current_date}")

    # Web Search
    elif "search for" in command:
        query = command.replace("search for", "").strip()
        if query:
            speak(f"Searching for {query} on Google.")
            webbrowser.open(f"https://www.google.com/search?q={query}")
        else:
            speak("What would you like me to search for?")

    # Wikipedia Summary
    elif "tell me about" in command or "who is" in command or "what is" in command:
        # Avoid triggering if it's a simple "what is the time" or math
        if "time" not in command and not re.search(r'\d+', command):
            topic = command.replace("tell me about", "").replace("who is", "").replace("what is", "").strip()
            if topic:
                try:
                    speak(f"Looking up {topic} on Wikipedia.")
                    summary = wikipedia.summary(topic, sentences=2)
                    speak(f"According to Wikipedia: {summary}")
                except wikipedia.exceptions.DisambiguationError as e:
                    speak(f"There are multiple entries for {topic}. Could you be more specific?")
                except wikipedia.exceptions.PageError:
                    speak(f"I couldn't find any information about {topic}.")
                except Exception:
                    speak("I'm having trouble connecting to Wikipedia right now.")
            else:
                speak("What would you like to know about?")
        elif re.search(r'\d+', command) and any(op in command for op in ["plus", "minus", "times", "divided by"]):
            # This is a math command, let the math handler catch it if it didn't already
            math_result = handle_math(command)
            if math_result:
                speak(math_result)

    # Math calculations (redundant check but safe)
    elif any(op in command for op in ["plus", "minus", "times", "multiplied by", "divided by", "calculate"]):
        math_result = handle_math(command)
        if math_result:
            speak(math_result)
        else:
            speak("I heard a math request but couldn't parse the numbers. Try saying 'What is 5 plus 10?'")

    # System Controls
    elif "open" in command or "launch" in command:
        app = command.replace("open", "").replace("launch", "").strip()
        system = platform.system()
        
        if "notepad" in app:
            if system == "Windows": subprocess.Popen(["notepad.exe"])
            speak("Opening Notepad.")
        elif "chrome" in app:
            if system == "Windows": subprocess.Popen(["start", "chrome"], shell=True)
            elif system == "Darwin": subprocess.Popen(["open", "-a", "Google Chrome"])
            else: subprocess.Popen(["google-chrome"])
            speak("Opening Chrome.")
        elif "calculator" in app:
            if system == "Windows": subprocess.Popen(["calc.exe"])
            speak("Opening Calculator.")
        elif "folder" in app or "directory" in app:
            path = os.path.expanduser("~") # Default to home
            if system == "Windows": os.startfile(path)
            elif system == "Darwin": subprocess.Popen(["open", path])
            else: subprocess.Popen(["xdg-open", path])
            speak("Opening your home directory.")
        else:
            speak(f"I'm not sure how to open {app} on this system.")

    elif "volume" in command:
        if "up" in command:
            if platform.system() == "Windows":
                # Using simple VBScript for volume if pycaw isn't ready
                os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]175)")
            speak("Increasing volume.")
        elif "down" in command:
            if platform.system() == "Windows":
                os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]174)")
            speak("Decreasing volume.")
        elif "mute" in command:
            if platform.system() == "Windows":
                os.system("powershell -Command (New-Object -ComObject WScript.Shell).SendKeys([char]173)")
            speak("Toggling mute.")

    elif "create folder" in command or "make folder" in command:
        folder_name = command.replace("create folder", "").replace("make folder", "").strip()
        if not folder_name: folder_name = "New Voice Folder"
        try:
            os.makedirs(folder_name, exist_ok=True)
            speak(f"Folder {folder_name} created successfully.")
        except Exception as e:
            speak(f"Could not create folder. Error: {e}")

    elif "exit" in command or "stop" in command or "bye" in command:
        speak("Goodbye! Have a great day.")
        return False

    # Learn Mode
    elif "teach you" in command or "learn mode" in command or "new command" in command:
        speak("Entering learn mode. What is the voice trigger phrase you want to use?")
        trigger = listen()
        if trigger:
            speak(f"I heard: {trigger}. What should I do when I hear this? Say 'Open website', 'Open folder', or 'Run script'.")
            choice = listen()
            if choice:
                action_type = ""
                if "website" in choice or "url" in choice: action_type = "url"
                elif "folder" in choice or "path" in choice: action_type = "path"
                elif "script" in choice or "command" in choice: action_type = "script"
                
                if action_type:
                    speak(f"Please say the {action_type} I should use.")
                    # In a real scenario, URLs might be better typed, but we'll try voice
                    action = listen()
                    if action:
                        # Simple cleanup for common voice errors
                        if action_type == "url" and "dot" in action:
                            action = action.replace(" dot ", ".")
                        
                        save_custom_command(trigger, action_type, action)
                        speak(f"Command learned! I will now {action_type} {action} when you say {trigger}.")
                else:
                    speak("I didn't understand the action type. Learning cancelled.")
        else:
            speak("I didn't hear a trigger phrase. Learning cancelled.")

    # Custom Command Execution
    else:
        custom_commands = load_custom_commands()
        for cmd in custom_commands:
            if cmd["trigger"] in command:
                speak(f"Executing custom command: {cmd['trigger']}")
                if cmd["action_type"] == "url":
                    webbrowser.open(cmd["action"])
                elif cmd["action_type"] == "path":
                    if platform.system() == "Windows": os.startfile(cmd["action"])
                    else: subprocess.Popen(["open", cmd["action"]])
                elif cmd["action_type"] == "script":
                    subprocess.Popen(cmd["action"], shell=True)
                return True
        
        speak(f"I heard you say: {command}. I can help with greetings, time, date, math, system controls, or you can teach me a new command.")
        
    return True

def main():
    speak("Assistant initialized. Say 'Hello' to start or 'Exit' to quit.")
    
    running = True
    while running:
        command = listen()
        running = process_command(command)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAssistant stopped by user.")
        sys.exit()
