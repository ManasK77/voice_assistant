# 🎙️ VoiceAssist — Python Voice Assistant System

> A comprehensive, modular voice assistant built in Python that allows users to control their computer entirely through natural language voice commands.

---

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Directory Structure](#directory-structure)
4. [Module Specifications](#module-specifications)
5. [Complete Implementation Guide](#complete-implementation-guide)
6. [Dependencies & Installation](#dependencies--installation)
7. [Configuration](#configuration)
8. [Command Reference](#command-reference)
9. [Error Handling Strategy](#error-handling-strategy)
10. [Platform Notes](#platform-notes)
11. [Testing Checklist](#testing-checklist)

---

## Project Overview

VoiceAssist is a voice-controlled desktop assistant that:

- Listens continuously for voice commands via microphone
- Converts speech to text using Google Speech Recognition
- Detects user intent from natural language
- Routes commands to the correct module
- Executes system actions and returns spoken responses
- Provides a minimal GUI dashboard (tkinter) showing status, logs, and active module

**Entry Point:** `main.py`  
**GUI:** `gui/dashboard.py` (tkinter-based, optional overlay)  
**Config:** `config.py`

---

## System Architecture

```
User speaks
    │
    ▼
[Microphone Input]
    │
    ▼
[speech_recognition] ──► raw text string
    │
    ▼
[Intent Detector] ──► module_name + parsed_args
    │
    ├──► core/info_ops.py       (web, wikipedia, weather, time)
    ├──► core/system_ops.py     (volume, brightness, apps)
    ├──► core/file_ops.py       (files, folders)
    ├──► core/camera_skill.py   (webcam, photo)
    ├──► core/screenshot_ops.py (screenshot, OCR)
    ├──► core/system_status.py  (CPU, RAM, disk)
    └──► core/productivity.py   (calculator, todos, reminders)
         │
         ▼
    [Response text]
         │
         ▼
    [pyttsx3 TTS] ──► spoken response
         │
         ▼
    [GUI log update]
```

---

## Directory Structure

```
voiceassist/
│
├── main.py                  # Entry point — starts listener loop + GUI
├── config.py                # All constants, API keys, paths, defaults
├── intent_engine.py         # NLP intent detection + command routing
├── voice_io.py              # Speech recognition + TTS wrapper
│
├── core/
│   ├── __init__.py
│   ├── info_ops.py          # Web search, Wikipedia, weather, time/date
│   ├── system_ops.py        # Volume, brightness, open/close apps
│   ├── file_ops.py          # Create/read/delete files and folders
│   ├── camera_skill.py      # Webcam capture, optional object detection
│   ├── screenshot_ops.py    # Screenshots + OCR (pytesseract)
│   ├── system_status.py     # CPU, RAM, disk, temperature, task manager
│   └── productivity.py      # Calculator, to-do list, reminders
│
├── gui/
│   ├── __init__.py
│   └── dashboard.py         # tkinter GUI dashboard
│
├── data/
│   ├── todos.json           # Persistent to-do list storage
│   ├── reminders.json       # Persistent reminders storage
│   └── screenshots/         # Auto-created; saved screenshots go here
│
├── photos/                  # Auto-created; webcam captures go here
├── logs/
│   └── assistant.log        # Rolling log file
├── requirements.txt
└── README.md
```

---

## Module Specifications

---

### `config.py`

Store all tuneable constants here. Every other module imports from this file.

```python
# config.py

import os

# --- Paths ---
BASE_DIR        = os.path.dirname(os.path.abspath(__file__))
DATA_DIR        = os.path.join(BASE_DIR, "data")
PHOTOS_DIR      = os.path.join(BASE_DIR, "photos")
SCREENSHOTS_DIR = os.path.join(DATA_DIR, "screenshots")
LOGS_DIR        = os.path.join(BASE_DIR, "logs")
TODOS_FILE      = os.path.join(DATA_DIR, "todos.json")
REMINDERS_FILE  = os.path.join(DATA_DIR, "reminders.json")

# --- Speech Recognition ---
SR_LANGUAGE         = "en-IN"   # Change to "en-US" if needed
SR_ENERGY_THRESHOLD = 300       # Mic sensitivity (lower = more sensitive)
SR_PAUSE_THRESHOLD  = 0.8       # Seconds of silence before phrase ends
SR_TIMEOUT          = 5         # Seconds to wait for speech start
SR_PHRASE_LIMIT     = 10        # Max seconds for a single command

# --- TTS (pyttsx3) ---
TTS_RATE   = 175   # Words per minute
TTS_VOLUME = 0.9   # 0.0 to 1.0
TTS_VOICE_INDEX = 0  # 0 = first available voice

# --- Assistant ---
WAKE_WORD   = "friday"   # Optional wake word (set to None to disable)
ASSISTANT_NAME = "VoiceAssist"

# --- API Keys ---
WEATHER_API_KEY = "YOUR_OPENWEATHERMAP_API_KEY"   # https://openweathermap.org/api
DEFAULT_CITY    = "Mumbai"   # Fallback city for weather

# --- GUI ---
GUI_ENABLED = False
GUI_WIDTH   = 420
GUI_HEIGHT  = 580
GUI_THEME   = "dark"   # "dark" or "light"

# --- Logging ---
LOG_LEVEL = "INFO"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 3

# Auto-create required directories
for _dir in [DATA_DIR, PHOTOS_DIR, SCREENSHOTS_DIR, LOGS_DIR]:
    os.makedirs(_dir, exist_ok=True)
```

---

### `voice_io.py`

Wraps all input/output: microphone listening and text-to-speech.

**Class: `VoiceIO`**

```python
class VoiceIO:
    def __init__(self):
        # Initialize pyttsx3 engine
        # Apply TTS_RATE, TTS_VOLUME, TTS_VOICE_INDEX from config
        # Initialize speech_recognition Recognizer with energy_threshold, pause_threshold

    def speak(self, text: str) -> None:
        # Print text to console with [ASSISTANT] prefix
        # Call engine.say(text) then engine.runAndWait()
        # Update GUI log if GUI is active

    def listen(self) -> str | None:
        # Open Microphone with sr.Microphone() as source
        # Call recognizer.adjust_for_ambient_noise(source, duration=0.5)
        # Call recognizer.listen(source, timeout=SR_TIMEOUT, phrase_time_limit=SR_PHRASE_LIMIT)
        # Call recognizer.recognize_google(audio, language=SR_LANGUAGE)
        # Return lowercase stripped text, or None on failure
        # Handle sr.WaitTimeoutError → return None silently
        # Handle sr.UnknownValueError → return None silently
        # Handle sr.RequestError → speak("Speech service unavailable") → return None

    def listen_continuous(self, callback: callable) -> None:
        # Infinite loop calling self.listen()
        # If result is not None, call callback(result)
        # Sleep 0.1s between iterations
```

---

### `intent_engine.py`

Converts raw text into (module, action, args) tuples via keyword matching.

**Design:** Use a dictionary-based keyword matcher. No ML required.

```python
# Structure of intent map:
INTENT_MAP = {
    "time":        {"keywords": ["time", "what time", "current time"],              "module": "info",       "action": "get_time"},
    "date":        {"keywords": ["date", "today's date", "what day"],               "module": "info",       "action": "get_date"},
    "weather":     {"keywords": ["weather", "temperature", "forecast", "how hot"],  "module": "info",       "action": "get_weather"},
    "search":      {"keywords": ["search for", "search", "look up", "who is", "what is", "tell me about", "what"], "module": "info", "action": "web_search"},
    "volume_up":   {"keywords": ["volume up", "increase volume", "louder"],         "module": "system",     "action": "volume_up"},
    "volume_down": {"keywords": ["volume down", "decrease volume", "quieter"],      "module": "system",     "action": "volume_down"},
    "mute":        {"keywords": ["mute", "silence", "quiet"],                       "module": "system",     "action": "mute"},
    "brightness_up":{"keywords":["brightness up", "brighter", "increase brightness"],"module":"system",     "action": "brightness_up"},
    "brightness_down":{"keywords":["brightness down","dimmer","decrease brightness"],"module":"system",     "action": "brightness_down"},
    "open_app":    {"keywords": ["open", "launch", "start"],                        "module": "system",     "action": "open_app"},
    "close_app":   {"keywords": ["close", "kill", "exit", "terminate"],             "module": "system",     "action": "close_app"},
    "create_file": {"keywords": ["create file", "make file", "new file"],           "module": "file",       "action": "create_file"},
    "read_file":   {"keywords": ["read file", "open file", "show file"],            "module": "file",       "action": "read_file"},
    "delete_file": {"keywords": ["delete file", "remove file"],                     "module": "file",       "action": "delete_file"},
    "list_files":  {"keywords": ["list files", "show files", "what files"],         "module": "file",       "action": "list_files"},
    "create_folder":{"keywords":["create folder","make folder","new folder"],       "module": "file",       "action": "create_folder"},
    "take_photo":  {"keywords": ["take photo", "take a photo", "capture photo", "capture a photo", "take picture", "take a picture", "selfie"], "module": "camera", "action": "capture_photo"},
    "screenshot":  {"keywords": ["screenshot", "capture screen", "screen capture"], "module": "screenshot", "action": "take_screenshot"},
    "read_screen": {"keywords": ["read screen", "what's on screen", "ocr"],         "module": "screenshot", "action": "read_screen_text"},
    "cpu":         {"keywords": ["cpu", "processor usage", "cpu usage"],            "module": "status",     "action": "cpu_usage"},
    "ram":         {"keywords": ["ram", "memory usage", "ram usage"],               "module": "status",     "action": "ram_usage"},
    "disk":        {"keywords": ["disk", "storage", "disk usage"],                  "module": "status",     "action": "disk_usage"},
    "system_status":{"keywords":["system status","performance","how is my computer"],"module":"status",     "action": "full_status"},
    "task_manager":{"keywords": ["task manager", "open task manager"],              "module": "status",     "action": "open_task_manager"},
    "calculate":   {"keywords": ["calculate", "what is", "compute", "evaluate"],    "module": "productivity","action": "calculate"},
    "add_todo":    {"keywords": ["add task", "add to-do", "remember to", "add todo"],"module":"productivity","action": "add_todo"},
    "show_todos":  {"keywords": ["show tasks", "my tasks", "to-do list", "what are my tasks"],"module":"productivity","action": "show_todos"},
    "clear_todos": {"keywords": ["clear tasks", "delete all tasks"],                "module": "productivity","action": "clear_todos"},
    "set_reminder":{"keywords": ["remind me", "set reminder", "set an alarm"],      "module": "productivity","action": "set_reminder"},
    "stop":        {"keywords": ["stop", "quit", "goodbye", "exit", "bye"],         "module": "core",       "action": "stop"},
}

class IntentEngine:
    def detect(self, text: str) -> dict:
        # Normalize text to lowercase
        # Iterate INTENT_MAP, check if any keyword is substring of text
        # Return {"module": ..., "action": ..., "raw_text": text}
        # If no match found, return {"module": "unknown", "action": "unknown", "raw_text": text}

    def extract_arg(self, text: str, keywords: list | str) -> str:
        # Strip the matched keyword from text and return remainder
        # Example: "open calculator" with keyword "open" → "calculator"
        # Strip leading/trailing whitespace from result
```

---

### `core/info_ops.py`

**Functions to implement:**

```python
def get_time() -> str:
    # Return: "The current time is HH:MM AM/PM"
    # Use: datetime.datetime.now().strftime("%I:%M %p")

def get_date() -> str:
    # Return: "Today is Monday, 7 April 2025"
    # Use: datetime.datetime.now().strftime("%A, %d %B %Y")

def get_weather(city: str = config.DEFAULT_CITY) -> str:
    # Call OpenWeatherMap API:
    # URL: f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    # Parse: data["main"]["temp"], data["weather"][0]["description"]
    # Return: "The weather in {city} is {description} with a temperature of {temp}°C"
    # On error (no key, network fail): return "Weather service unavailable. Please set your API key in config.py"

def wikipedia_summary(query: str) -> str:
    # import wikipedia
    # Set wikipedia.set_lang("en")
    # Try: wikipedia.summary(query, sentences=2)
    # On wikipedia.exceptions.DisambiguationError → try first option
    # On wikipedia.exceptions.PageError → return "No Wikipedia page found for {query}"
    # Return first 2 sentences of result

def web_search(query: str) -> str:
    # Open browser with: webbrowser.open(f"https://www.google.com/search?q={query}")
    # Return: "Searching Google for {query}"
    # import webbrowser
```

---

### `core/system_ops.py`

**Platform awareness:** This module must handle Windows, macOS, and Linux differences.

```python
import platform
import subprocess
import psutil

PLATFORM = platform.system()  # "Windows", "Darwin", "Linux"

def volume_up(step: int = 10) -> str:
    # Windows: use pycaw or os.system("nircmd.exe changesysvolume 6553")
    # macOS: subprocess.run(["osascript", "-e", f"set volume output volume (output volume of (get volume settings) + {step})"])
    # Linux: subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{step}%+"])
    # Return: "Volume increased"

def volume_down(step: int = 10) -> str:
    # Mirror of volume_up but decrease
    # Return: "Volume decreased"

def mute() -> str:
    # Windows: toggle mute via pycaw or nircmd
    # macOS: subprocess.run(["osascript", "-e", "set volume with output muted"])
    # Linux: subprocess.run(["amixer", "-D", "pulse", "sset", "Master", "toggle"])
    # Return: "System muted"

def brightness_up(step: int = 10) -> str:
    # Use screen_brightness_control: sbc.get_brightness(), sbc.set_brightness(min(current+step, 100))
    # Wrap in try/except (brightness control may fail on some monitors)
    # Return: "Brightness increased to {new_level}%"

def brightness_down(step: int = 10) -> str:
    # Mirror of brightness_up but decrease
    # Return: "Brightness decreased to {new_level}%"

def open_app(app_name: str) -> str:
    # Maintain a dict APP_MAP with common apps:
    APP_MAP = {
        "calculator":  {"Windows": "calc",      "Darwin": "Calculator",  "Linux": "gnome-calculator"},
        "notepad":     {"Windows": "notepad",    "Darwin": "TextEdit",    "Linux": "gedit"},
        "browser":     {"Windows": "start chrome","Darwin": "Google Chrome","Linux": "google-chrome"},
        "file manager":{"Windows": "explorer",   "Darwin": "Finder",      "Linux": "nautilus"},
        "terminal":    {"Windows": "cmd",        "Darwin": "Terminal",    "Linux": "gnome-terminal"},
        "paint":       {"Windows": "mspaint",    "Darwin": "Preview",     "Linux": "gimp"},
        "word":        {"Windows": "winword",    "Darwin": "Microsoft Word","Linux": "libreoffice --writer"},
        "excel":       {"Windows": "excel",      "Darwin": "Microsoft Excel","Linux": "libreoffice --calc"},
    }
    # Fuzzy match app_name against APP_MAP keys
    # Use subprocess.Popen or os.startfile (Windows) to open
    # If not found in map: try subprocess.Popen([app_name]) directly
    # Return: "Opening {app_name}" or "Could not find {app_name}"

def close_app(app_name: str) -> str:
    # Iterate psutil.process_iter(["name"])
    # Kill processes where app_name is substring of process name (case-insensitive)
    # Return: "Closed {app_name}" or "No running process found for {app_name}"
```

---

### `core/file_ops.py`

**Default working directory:** User's home directory (`os.path.expanduser("~")`)

```python
import os

DEFAULT_DIR = os.path.expanduser("~")

def create_file(filename: str, content: str = "", directory: str = DEFAULT_DIR) -> str:
    # Build full path: os.path.join(directory, filename)
    # Add .txt extension if no extension provided
    # Write content to file (UTF-8)
    # Return: "File {filename} created at {path}"

def read_file(filename: str, directory: str = DEFAULT_DIR) -> str:
    # Search for file in directory (and subdirectory one level deep if not found directly)
    # Read and return first 500 chars of content + "..." if truncated
    # On FileNotFoundError: return "File {filename} not found"
    # Return spoken version: "The file contains: {content}"

def delete_file(filename: str, directory: str = DEFAULT_DIR) -> str:
    # Locate file, call os.remove(path)
    # Return: "File {filename} deleted"
    # On error: "Could not delete {filename}: {reason}"

def list_files(directory: str = DEFAULT_DIR) -> str:
    # os.listdir(directory)
    # Filter to files only (not subdirs), or include both
    # Return: "Found {n} files: file1, file2, file3..."
    # Limit spoken list to 10 items max

def create_folder(folder_name: str, parent: str = DEFAULT_DIR) -> str:
    # os.makedirs(os.path.join(parent, folder_name), exist_ok=True)
    # Return: "Folder {folder_name} created"
```

---

### `core/camera_skill.py`

```python
import cv2
import datetime
import os
from config import PHOTOS_DIR

def capture_photo(filename: str = None) -> str:
    # If filename is None: generate timestamped name "photo_YYYYMMDD_HHMMSS.jpg"
    # cv2.VideoCapture(0) → open default webcam
    # Show preview window for 2 seconds (cv2.imshow / cv2.waitKey(2000))
    # cap.read() → grab frame
    # cv2.imwrite(os.path.join(PHOTOS_DIR, filename), frame)
    # cap.release(), cv2.destroyAllWindows()
    # Return: "Photo saved as {filename}"
    # On camera error (cap.isOpened() is False): return "No camera found"

def detect_objects(image_path: str) -> str:
    # OPTIONAL: Use OpenCV's pre-trained Haar cascades for face detection
    # Load cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    # Read image, convert to grayscale
    # detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)
    # Return: "Detected {n} face(s) in the image"
    # If no detection: "No faces detected"
    # This is lightweight — no deep learning required
```

---

### `core/screenshot_ops.py`

```python
import pyautogui
import pytesseract
from PIL import Image
import datetime
import os
from config import SCREENSHOTS_DIR

# On Windows: set Tesseract path if needed
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def take_screenshot(filename: str = None) -> str:
    # If filename is None: generate timestamped name "screenshot_YYYYMMDD_HHMMSS.png"
    # pyautogui.screenshot() → PIL Image object
    # Save to SCREENSHOTS_DIR/filename
    # Return: "Screenshot saved as {filename}"

def read_screen_text() -> str:
    # Take a screenshot (in memory, don't save)
    # pytesseract.image_to_string(screenshot_image)
    # Strip whitespace, truncate to 300 chars for TTS
    # Return: "The screen shows: {text}" or "Could not read any text from the screen"
```

---

### `core/system_status.py`

```python
import psutil
import platform
import subprocess
import datetime

def cpu_usage() -> str:
    # psutil.cpu_percent(interval=1)
    # Return: "CPU usage is {percent}%"

def ram_usage() -> str:
    # psutil.virtual_memory() → .percent, .used, .total
    # Convert bytes to GB: value / (1024**3)
    # Return: "RAM usage is {percent}% — {used:.1f} GB of {total:.1f} GB used"

def disk_usage(path: str = "/") -> str:
    # Windows: use "C:\\" as default path
    # psutil.disk_usage(path) → .percent, .used, .total
    # Return: "Disk usage is {percent}% — {used:.1f} GB of {total:.1f} GB used"

def get_temperature() -> str:
    # psutil.sensors_temperatures() → may return {} on Windows/macOS
    # If available: extract first temperature reading in Celsius
    # Return: "CPU temperature is {temp}°C" or "Temperature data not available on this system"

def get_fan_speed() -> str:
    # psutil.sensors_fans() → may return {} on most systems
    # Return fan RPM if available, else "Fan speed data not available on this system"

def full_status() -> str:
    # Combine cpu_usage + ram_usage + disk_usage into one spoken summary
    # Return: "System status: CPU at {x}%, RAM at {y}%, Disk at {z}%"

def open_task_manager() -> str:
    # Windows: subprocess.Popen(["taskmgr"])
    # macOS: subprocess.Popen(["open", "-a", "Activity Monitor"])
    # Linux: subprocess.Popen(["gnome-system-monitor"]) or ["htop"] in terminal
    # Return: "Opening task manager"
```

---

### `core/productivity.py`

```python
import json
import os
import datetime
import threading
from config import TODOS_FILE, REMINDERS_FILE

# --- Calculator ---

def calculate(expression: str) -> str:
    # Clean expression: remove words like "what is", "calculate", "compute"
    # Replace spoken words: "plus"→"+", "minus"→"-", "times"/"multiplied by"→"*", "divided by"→"/"
    # Replace "percent" → "/100", "squared" → "**2", "cubed" → "**3"
    # Use eval() with restricted globals: eval(expr, {"__builtins__": {}})
    # Wrap in try/except for invalid expressions
    # Return: "The answer is {result}" or "Could not calculate that"
    # SECURITY: Only allow digits and math operators in eval input

# --- To-Do List ---

def _load_todos() -> list:
    # Load from TODOS_FILE (JSON list of strings)
    # Return [] if file missing or corrupt

def _save_todos(todos: list) -> None:
    # Write JSON to TODOS_FILE

def add_todo(task: str) -> str:
    # Load todos, append task, save
    # Return: "Task added: {task}"

def show_todos() -> str:
    # Load todos
    # If empty: return "Your to-do list is empty"
    # Return: "You have {n} tasks: 1. {task1}, 2. {task2}..."

def clear_todos() -> str:
    # Save empty list to TODOS_FILE
    # Return: "All tasks cleared"

# --- Reminders ---

def _load_reminders() -> list:
    # Load from REMINDERS_FILE (list of {"text": str, "time": ISO string, "done": bool})
    # Return [] if missing

def _save_reminders(reminders: list) -> None:
    # Write JSON to REMINDERS_FILE

def set_reminder(text: str, minutes: int = 1) -> str:
    # Parse minutes from text: look for number before "minute(s)"
    # Default to 1 minute if not found
    # Store reminder with trigger time = now + minutes
    # Start a daemon thread: threading.Timer(seconds, _fire_reminder, args=[text, speak_fn])
    # Return: "Reminder set for {minutes} minute(s): {text}"

def _fire_reminder(text: str, speak_fn: callable) -> None:
    # Call speak_fn(f"Reminder: {text}")
    # Update reminder as done=True in REMINDERS_FILE

def check_reminders(speak_fn: callable) -> None:
    # Called periodically from main loop
    # Load reminders, check if any are past due and not done
    # Fire them and mark done
```

---

### `main.py`

```python
"""
VoiceAssist — Main Entry Point

Starts the continuous voice listening loop and optionally launches the GUI.
"""

import threading
import time
import logging
from logging.handlers import RotatingFileHandler

import config
from voice_io import VoiceIO
from intent_engine import IntentEngine
from core import info_ops, system_ops, file_ops, camera_skill, screenshot_ops, system_status, productivity

# --- Logging Setup ---
logger = logging.getLogger("VoiceAssist")
# Configure RotatingFileHandler to config.LOGS_DIR/assistant.log

# --- Module Router ---
def route_command(intent: dict, voice: VoiceIO) -> None:
    module  = intent["module"]
    action  = intent["action"]
    raw     = intent["raw_text"]

    if module == "core" and action == "stop":
        voice.speak("Goodbye!")
        raise SystemExit

    elif module == "info":
        if action == "get_time":       response = info_ops.get_time()
        elif action == "get_date":     response = info_ops.get_date()
        elif action == "get_weather":  response = info_ops.get_weather()
        elif action == "web_search":
            query = intent_engine.extract_arg(raw, ["search for", "search", "look up", "tell me about", "who is", "what is", "what"])
            response = info_ops.web_search(query)

    elif module == "system":
        if action == "volume_up":       response = system_ops.volume_up()
        elif action == "volume_down":   response = system_ops.volume_down()
        elif action == "mute":          response = system_ops.mute()
        elif action == "brightness_up": response = system_ops.brightness_up()
        elif action == "brightness_down":response = system_ops.brightness_down()
        elif action == "open_app":
            app = intent_engine.extract_arg(raw, ["open", "launch", "start"])
            response = system_ops.open_app(app)
        elif action == "close_app":
            app = intent_engine.extract_arg(raw, ["close", "kill", "exit", "terminate"])
            response = system_ops.close_app(app)

    elif module == "file":
        if action == "create_file":
            name = intent_engine.extract_arg(raw, ["create file", "make file", "new file"])
            response = file_ops.create_file(name)
        elif action == "read_file":
            name = intent_engine.extract_arg(raw, ["read file", "open file", "show file"])
            response = file_ops.read_file(name)
        elif action == "delete_file":
            name = intent_engine.extract_arg(raw, ["delete file", "remove file"])
            response = file_ops.delete_file(name)
        elif action == "list_files":    response = file_ops.list_files()
        elif action == "create_folder":
            name = intent_engine.extract_arg(raw, ["create folder", "make folder", "new folder"])
            response = file_ops.create_folder(name)

    elif module == "camera":
        if action == "capture_photo":  response = camera_skill.capture_photo()

    elif module == "screenshot":
        if action == "take_screenshot": response = screenshot_ops.take_screenshot()
        elif action == "read_screen_text": response = screenshot_ops.read_screen_text()

    elif module == "status":
        if action == "cpu_usage":        response = system_status.cpu_usage()
        elif action == "ram_usage":      response = system_status.ram_usage()
        elif action == "disk_usage":     response = system_status.disk_usage()
        elif action == "full_status":    response = system_status.full_status()
        elif action == "open_task_manager": response = system_status.open_task_manager()

    elif module == "productivity":
        if action == "calculate":
            expr = intent_engine.extract_arg(raw, ["calculate", "what is", "compute"])
            response = productivity.calculate(expr)
        elif action == "add_todo":
            task = intent_engine.extract_arg(raw, ["add task", "add to-do", "remember to", "add todo"])
            response = productivity.add_todo(task)
        elif action == "show_todos":    response = productivity.show_todos()
        elif action == "clear_todos":   response = productivity.clear_todos()
        elif action == "set_reminder":
            response = productivity.set_reminder(raw, speak_fn=voice.speak)

    else:
        response = "I didn't understand that command. Please try again."

    voice.speak(response)
    logger.info(f"CMD: {raw!r} → {module}.{action} → {response!r}")

# --- Main Loop ---
def main():
    voice = VoiceIO()
    engine = IntentEngine()

    # GUI is initialized separately if needed
    # (Removed from main thread loop)

    voice.speak(f"Hello! I am {config.ASSISTANT_NAME}. How can I help you?")

    while True:
        try:
            text = voice.listen()
            if text is None:
                continue

            # Optional wake word filter
            if config.WAKE_WORD and config.WAKE_WORD not in text:
                continue

            if config.WAKE_WORD:
                text = text.replace(config.WAKE_WORD, "").strip()

            logger.info(f"Heard: {text!r}")
            intent = engine.detect(text)
            route_command(intent, voice)

            # Check pending reminders
            productivity.check_reminders(voice.speak)

        except SystemExit:
            break
        except KeyboardInterrupt:
            voice.speak("Shutting down.")
            break
        except Exception as e:
            logger.error(f"Unhandled error: {e}", exc_info=True)
            voice.speak("Something went wrong. Please try again.")

if __name__ == "__main__":
    main()
```

---

### `gui/dashboard.py`

Build a dark-themed tkinter window with:

```
┌─────────────────────────────────────┐
│  🎙️  VoiceAssist          [● LIVE]  │
├─────────────────────────────────────┤
│  Status: Listening...               │
│  Last Command: "open calculator"    │
│  Last Response: "Opening calculator"│
├─────────────────────────────────────┤
│  📋 COMMAND LOG                     │
│  ┌─────────────────────────────┐    │
│  │ [10:34 AM] open calculator  │    │
│  │ [10:35 AM] what time is it  │    │
│  │ ...                         │    │
│  └─────────────────────────────┘    │
├─────────────────────────────────────┤
│  💻 CPU: 23%  🧠 RAM: 61%           │
│  💾 Disk: 45%                       │
├─────────────────────────────────────┤
│          [🔴 STOP]                  │
└─────────────────────────────────────┘
```

**Implementation notes:**

```python
import tkinter as tk
from tkinter import scrolledtext
import threading
import psutil
import time

class Dashboard:
    def __init__(self, voice_io_ref):
        self.voice = voice_io_ref
        self.root = tk.Tk()
        self.root.title("VoiceAssist")
        self.root.geometry(f"{config.GUI_WIDTH}x{config.GUI_HEIGHT}")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(False, False)

        # Build UI widgets here (labels, ScrolledText log, stats labels)
        # Use color scheme: bg="#1a1a2e", accent="#e94560", text="#eaeaea"

        # Status label (Listening / Processing / Speaking)
        # Last command label
        # Last response label
        # ScrolledText log widget (max 200 lines)
        # CPU / RAM / Disk live stats (update every 2s via after())
        # STOP button that calls root.quit() and sys.exit()

    def log(self, message: str):
        # Thread-safe log append to ScrolledText widget
        # Use self.root.after(0, ...) to update from non-main thread

    def update_status(self, status: str):
        # Update status label text ("Listening...", "Processing...", "Speaking...")

    def update_stats(self):
        # psutil.cpu_percent(), virtual_memory().percent, disk_usage().percent
        # Schedule next update: self.root.after(2000, self.update_stats)

    def run(self):
        self.update_stats()
        self.root.mainloop()
```

---

## Dependencies & Installation

### `requirements.txt`

```
SpeechRecognition>=3.10.0
pyttsx3>=2.90
pyautogui>=0.9.54
psutil>=5.9.0
opencv-python>=4.8.0
pytesseract>=0.3.10
wikipedia>=1.4.0
requests>=2.31.0
screen-brightness-control>=0.23.0
Pillow>=10.0.0
pycaw>=20240210       # Windows only — comment out on macOS/Linux
```

### Installation Steps

```bash
# 1. Clone or create project directory
mkdir voiceassist && cd voiceassist

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install system-level dependencies

# --- Windows ---
# Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki
# Download installer → install to C:\Program Files\Tesseract-OCR\

# --- macOS ---
brew install tesseract portaudio
pip install pyaudio

# --- Linux (Ubuntu/Debian) ---
sudo apt-get install -y tesseract-ocr portaudio19-dev python3-pyaudio
pip install pyaudio

# 5. Get OpenWeatherMap API key (free tier)
# https://openweathermap.org/api → sign up → copy API key → paste in config.py

# 6. Run
python main.py
```

### Tesseract Path Configuration

Add to top of `screenshot_ops.py` if on Windows:

```python
import platform
if platform.system() == "Windows":
    pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

### pycaw (Windows Volume Control)

`pycaw` is Windows-only. Gate it with a platform check:

```python
import platform
if platform.system() == "Windows":
    from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
```

---

## Configuration

Edit `config.py` before running:

| Variable | Default | Description |
|---|---|---|
| `WEATHER_API_KEY` | `"YOUR_KEY"` | OpenWeatherMap free API key |
| `DEFAULT_CITY` | `"Mumbai"` | Fallback city for weather queries |
| `WAKE_WORD` | `"friday"` | Say this before commands. Set to `None` to disable |
| `SR_LANGUAGE` | `"en-IN"` | Speech recognition language/locale |
| `TTS_RATE` | `175` | TTS speaking speed (words per minute) |
| `GUI_ENABLED` | `False` | Show/hide the dashboard window |

---

## Command Reference

### Information

| Say | Action |
|---|---|
| "What time is it?" | Speaks current time |
| "What is today's date?" | Speaks current date |
| "What's the weather?" | Weather for DEFAULT_CITY |
| "What is Python?" | Opens Google in browser |
| "Search for climate change" | Opens Google in browser |

### System Operations

| Say | Action |
|---|---|
| "Volume up" / "Make it louder" | Increases volume by 10% |
| "Volume down" / "Quieter" | Decreases volume by 10% |
| "Mute" | Toggles mute |
| "Brightness up" | Increases screen brightness by 10% |
| "Brightness down" | Decreases screen brightness by 10% |
| "Open calculator" | Launches calculator app |
| "Open notepad" | Launches text editor |
| "Close chrome" | Kills process named 'chrome' |

### File Management

| Say | Action |
|---|---|
| "Create file notes" | Creates notes.txt in home dir |
| "Read file notes" | Reads and speaks notes.txt |
| "Delete file notes" | Deletes notes.txt |
| "List files" | Lists files in home directory |
| "Create folder projects" | Creates projects/ in home dir |

### Camera & Screen

| Say | Action |
|---|---|
| "Take a photo" | Captures webcam photo, saves to photos/ |
| "Take a screenshot" | Saves screenshot to data/screenshots/ |
| "Read the screen" | OCR → speaks text on screen |

### System Status

| Say | Action |
|---|---|
| "CPU usage" | Speaks CPU percent |
| "RAM usage" | Speaks memory stats |
| "Disk usage" | Speaks disk stats |
| "System status" | Speaks combined summary |
| "Open task manager" | Launches task manager |

### Productivity

| Say | Action |
|---|---|
| "Calculate 25 times 4" | Speaks result: 100 |
| "What is 144 divided by 12" | Speaks result: 12 |
| "Add task buy groceries" | Adds to to-do list |
| "Show my tasks" | Reads all to-do items |
| "Clear all tasks" | Empties to-do list |
| "Remind me to drink water in 5 minutes" | Sets 5-minute reminder |

### Control

| Say | Action |
|---|---|
| "Stop" / "Quit" / "Goodbye" | Shuts down the assistant |

---

## Error Handling Strategy

Apply this pattern in every module function:

```python
def some_operation(arg: str) -> str:
    try:
        # ... do the work ...
        return "Success message"
    except SpecificException as e:
        logger.warning(f"Expected failure in some_operation: {e}")
        return "Friendly fallback message for TTS"
    except Exception as e:
        logger.error(f"Unexpected error in some_operation: {e}", exc_info=True)
        return "Sorry, something went wrong with that operation"
```

**Rules:**
- Functions must ALWAYS return a string (never raise to main loop)
- Log warnings for expected failures (network down, file not found)
- Log errors with `exc_info=True` for unexpected failures
- Return short, speakable strings (avoid technical jargon in responses)
- TTS responses should be under 50 words where possible

---

## Platform Notes

### Windows
- Volume: Use `pycaw` library (imported conditionally)
- Task Manager: `taskmgr`
- App opening: `os.startfile()` preferred over `subprocess`
- Tesseract: Must be installed separately and path configured

### macOS
- Volume: `osascript` AppleScript commands
- Brightness: `screen_brightness_control` may require permissions
- Task Manager equivalent: Activity Monitor
- Tesseract: Install via Homebrew (`brew install tesseract`)

### Linux
- Volume: `amixer` or `pactl` (PulseAudio)
- Brightness: `xrandr` or `screen_brightness_control`
- Task Manager: `gnome-system-monitor` or `xterm -e htop`
- Tesseract: Install via `apt-get`

---

## Testing Checklist

Run through these after initial build:

- [ ] `python main.py` starts without errors
- [ ] "What time is it?" → correct time spoken
- [ ] "What's the weather?" → weather spoken (requires API key) or fallback message
- [ ] "What is Albert Einstein?" → Performs a web search
- [ ] "Volume up" → system volume increases
- [ ] "Volume down" → system volume decreases
- [ ] "Open calculator" → calculator app opens
- [ ] "Close calculator" → calculator process terminates
- [ ] "Create file test" → test.txt created in home dir
- [ ] "Read file test" → file contents spoken
- [ ] "Delete file test" → file removed
- [ ] "List files" → list of files spoken
- [ ] "Take a photo" → photo saved in photos/ folder
- [ ] "Take a screenshot" → screenshot saved in data/screenshots/
- [ ] "Read screen" → visible text spoken
- [ ] "CPU usage" → percentage spoken
- [ ] "System status" → combined summary spoken
- [ ] "Calculate 10 times 10" → "The answer is 100" spoken
- [ ] "Add task finish report" → task saved and confirmed
- [ ] "Show my tasks" → all tasks read aloud
- [ ] "Remind me in 1 minute to stretch" → reminder fires after ~60 seconds
- [ ] "Stop" → graceful shutdown
- [ ] GUI shows live stats updating every 2 seconds
- [ ] GUI log appends each command in real time
- [ ] Unknown command → friendly fallback spoken

---

## Quick Start

```bash
# After completing installation:
python main.py

# Say: "Friday, what time is it?"
# Say: "Friday, open calculator"
# Say: "Friday, system status"
# Say: "Friday, stop"
```

---

*Built with Python 3.10+ · Modular architecture · Cross-platform (Windows / macOS / Linux)*
