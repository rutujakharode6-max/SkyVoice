# Premium GUI Voice Assistant

This is the comprehensive version of the voice assistant, featuring a modern graphical user interface, wake-word detection, and advanced API integrations.

## Features
- **Graphical User Interface**: Built with `customtkinter` for a sleek, dark-themed experience.
- **Voice Wave Animation**: Real-time visual feedback when the assistant is listening or speaking.
- **Wake-Word Detection**: Responds to **"Hey Assistant"** for hands-free interaction.
- **Continuous Listening**: Monitors the environment for the wake-word in the background.
- **API Integrations**: Fetches real-time **Weather** and **News** (requires API keys).
- **Command History**: Displays a scrollable log of all interactions.
- **All Previous Features**: Includes math, system controls, web search, Wikipedia lookup, and custom commands.

## Setup & API Keys
1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure APIs**:
   Open `assistant_gui.py` and replace the placeholders for:
   - `self.weather_api_key`: Get one from [OpenWeatherMap](https://openweathermap.org/api).
   - `self.news_api_key`: Get one from [NewsAPI](https://newsapi.org/).

## Running the App
```bash
python assistant_gui.py
```

## Usage
- Say **"Hey Assistant"** to wake it up.
- Ask for weather: *"What's the weather in Tokyo?"*
- Ask for news: *"Tell me the latest news."*
- View your interaction history directly in the GUI window.
