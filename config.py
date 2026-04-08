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
WEATHER_API_KEY = "58b5969f958e5f4b595de10d20a4950a"   # https://openweathermap.org/api
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
