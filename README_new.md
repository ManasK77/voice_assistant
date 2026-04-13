# 🎙️ VoiceAssist — Dual-Interface HCI Research Platform

> A modular desktop assistant that implements **both a voice-first interface and a full-featured GUI interface** with identical functionality — built to rigorously compare the two interaction paradigms across efficiency, cognitive load, and user preference.

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)]()
[![HCI](https://img.shields.io/badge/Course-Human--Computer%20Interaction-blueviolet?style=flat-square)]()

---

## 📖 Overview

VoiceAssist is a Python-based desktop assistant built as an HCI research platform. It exposes **two fully independent interaction interfaces** — a **voice-only interface** and a **GUI interface** — both backed by the same core task execution engine. Every feature available through voice is equally accessible through the GUI, and vice versa.

The project's primary research goal is a **controlled within-subjects comparison** of voice interaction vs. GUI interaction, measuring:

- **Task completion time** (efficiency)
- **Error rate** (reliability)
- **NASA-TLX cognitive load score** (mental effort)
- **User preference** (SUS questionnaire + qualitative feedback)

Both interfaces are designed to be **Nielsen Heuristic-compliant** (all 10 heuristics), making the comparison methodologically sound — any performance differences reflect genuine interaction modality effects, not design quality differences.

The project supports over **35 intents** across 7 task domains. The voice interface processes speech in real time via Google STT and responds via pyttsx3 TTS. The GUI interface provides click/keyboard interaction through a tkinter-based window that mirrors all voice capabilities through visual controls.

---

## ✨ Feature Parity Matrix

Both interfaces support the full feature set. The table below documents every capability and how it is surfaced in each modality.

| Domain | Capability | Voice Trigger | GUI Element |
|---|---|---|---|
| 🌐 Information | Current time | `"What time is it"` | Button: **Time** |
| 🌐 Information | Current date | `"What's the date"` | Button: **Date** |
| 🌐 Information | Weather | `"Weather in [city]"` | Input + Button: **Weather** |
| 🌐 Information | Wikipedia summary | `"Wikipedia [topic]"` | Input + Button: **Wiki Search** |
| 🌐 Information | Web search | `"Search for [query]"` | Input + Button: **Web Search** |
| 🖥️ System | Volume up | `"Volume up"` | Slider or Button: **Vol +** |
| 🖥️ System | Volume down | `"Volume down"` | Slider or Button: **Vol −** |
| 🖥️ System | Mute | `"Mute"` | Toggle Button: **Mute** |
| 🖥️ System | Brightness up | `"Brightness up"` | Slider or Button: **Bright +** |
| 🖥️ System | Brightness down | `"Brightness down"` | Slider or Button: **Bright −** |
| 🖥️ System | Launch app | `"Open [app name]"` | Input + Button: **Launch** |
| 🖥️ System | Close app | `"Close [app name]"` | Input + Button: **Terminate** |
| 📁 Files | Create file | `"Create file [name]"` | Input + Button: **New File** |
| 📁 Files | Read file | `"Read file [name]"` | Input + Button: **Read File** |
| 📁 Files | Delete file | `"Delete file [name]"` | Input + Button: **Delete File** |
| 📁 Files | List files | `"List files"` | Button: **List Files** |
| 📁 Files | Create folder | `"Create folder [name]"` | Input + Button: **New Folder** |
| ✅ Productivity | Calculator | `"Calculate [expression]"` | Input + Button: **Calculate** |
| ✅ Productivity | Add to-do | `"Add task [task]"` | Input + Button: **Add Task** |
| ✅ Productivity | Show to-dos | `"Show tasks"` | Button: **View Tasks** |
| ✅ Productivity | Clear to-dos | `"Clear tasks"` | Button: **Clear Tasks** |
| ✅ Productivity | Set reminder | `"Remind me to [task] in [N] minutes"` | Input + Spinner + Button: **Set Reminder** |
| 📷 Camera | Capture photo | `"Take a photo"` | Button: **Capture Photo** |
| 📷 Camera | Take screenshot | `"Take screenshot"` | Button: **Screenshot** |
| 📷 Camera | OCR screen | `"Read screen"` | Button: **OCR Screen** |
| 📊 System Status | CPU usage | `"CPU usage"` | Button: **CPU** / Live panel |
| 📊 System Status | RAM usage | `"RAM usage"` | Button: **RAM** / Live panel |
| 📊 System Status | Disk usage | `"Disk usage"` | Button: **Disk** / Live panel |
| 📊 System Status | Task manager | `"Open task manager"` | Button: **Task Manager** |

---

## 🗂️ Project Structure

```
VoiceAssist/
│
├── main.py                    # Entry point — launches voice mode, GUI mode, or both
├── config.py                  # All configurable parameters
│
├── voice_io.py                # Voice I/O — SpeechRecognition + pyttsx3 TTS
├── intent_engine.py           # Intent detection — INTENT_MAP keyword classifier (35+ intents)
│
├── core/                      # Shared task execution engine (used by BOTH interfaces)
│   ├── info_ops.py            # Time, date, weather, Wikipedia, web search
│   ├── system_ops.py          # Volume, brightness, app launch/termination (cross-platform)
│   ├── file_ops.py            # File create, read, delete, list; folder create
│   ├── camera_skill.py        # Webcam photo capture with optional face detection
│   ├── screenshot_ops.py      # Screenshot + OCR via pytesseract
│   ├── system_status.py       # CPU / RAM / disk usage reporting
│   └── productivity.py        # Calculator, to-do list (JSON), reminders (threaded timer)
│
├── interfaces/
│   ├── voice_interface.py     # Voice interaction loop — wake word, STT, intent, TTS response
│   └── gui_interface.py       # Full tkinter GUI — all 35+ intents as interactive controls
│
├── research/
│   ├── metrics_logger.py      # Records per-task timestamps, error counts, interface mode
│   ├── nasa_tlx.py            # In-app NASA-TLX questionnaire (post-session)
│   ├── sus_survey.py          # In-app SUS questionnaire (post-session)
│   └── session_manager.py     # Counterbalances interface order, manages participant sessions
│
├── data/
│   ├── todos.json             # Persistent to-do list
│   ├── reminders.json         # Reminder storage with completion tracking
│   ├── screenshots/           # Saved screenshots
│   └── research_logs/         # Per-participant CSV logs for statistical analysis
│
├── photos/                    # Saved webcam photos
├── logs/                      # Rotating command and error logs
└── requirements.txt
```

---

## ⚙️ Installation

### Prerequisites

- Python 3.10 or higher
- A working microphone (required for voice interface)
- Internet connection (for STT and weather)
- [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) (for OCR features)

### 1. Clone the repository

```bash
git clone https://github.com/your-username/voiceassist.git
cd voiceassist
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Install Tesseract OCR

| OS | Command |
|---|---|
| Windows | Download from [tesseract-ocr/tesseract](https://github.com/tesseract-ocr/tesseract) |
| macOS | `brew install tesseract` |
| Linux | `sudo apt install tesseract-ocr` |

> **Windows only:** Set path in `config.py`:
> ```python
> TESSERACT_PATH = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
> ```

### 4. Configure settings

Edit `config.py`:

```python
LANGUAGE = "en-IN"               # Speech recognition language
WAKE_WORD = "hey assist"         # Set to None to disable
TTS_RATE = 175                   # TTS speaking rate (wpm)
TTS_VOLUME = 0.9                 # TTS volume (0.0–1.0)
DEFAULT_CITY = "Mumbai"          # Default city for weather
OPENWEATHERMAP_API_KEY = "..."   # Free key at openweathermap.org
ENERGY_THRESHOLD = 300           # Mic sensitivity
PAUSE_THRESHOLD = 0.8            # Silence duration to end phrase (seconds)
```

### 5. Run VoiceAssist

```bash
# Launch voice-only interface
python main.py --mode voice

# Launch GUI interface
python main.py --mode gui

# Launch both simultaneously (for demonstration or parallel testing)
python main.py --mode both

# Launch in research/study mode (counterbalanced, logged)
python main.py --mode study --participant P01
```

---

## 🖥️ GUI Interface — Design Specification

The GUI interface is a **full-feature tkinter application** that exposes every assistant capability through visual controls. It is **not** a supplementary dashboard — it is a primary interaction channel with equal standing to the voice interface.

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  VoiceAssist  [mode: GUI]              [status badge]  [⚙ cfg]  │
├──────────────┬──────────────────────────────────────────────────┤
│              │                                                  │
│  NAVIGATION  │               MAIN CONTENT AREA                 │
│  SIDEBAR     │                                                  │
│              │  ┌─────────────────────────────────────────┐    │
│  Information │  │  Task Panel (changes per sidebar tab)   │    │
│  System      │  │                                         │    │
│  Files       │  │  [Input fields, buttons, result area]   │    │
│  Productivity│  │                                         │    │
│  Camera      │  └─────────────────────────────────────────┘    │
│  Monitoring  │                                                  │
│              │  ┌─────────────────────────────────────────┐    │
│              │  │  Response / Output Panel                │    │
│              │  │  (scrollable, timestamped log)          │    │
│              │  └─────────────────────────────────────────┘    │
├──────────────┴──────────────────────────────────────────────────┤
│  STATUS BAR: Last action  |  CPU: 12%  RAM: 4.1GB  |  🟢 Ready │
└─────────────────────────────────────────────────────────────────┘
```

### GUI-Specific Design Decisions

- Every action produces a visible result in the **Response Panel** (text output, success/error state, timestamps).
- System stats (CPU, RAM, Disk) update live in the status bar every 2 seconds.
- All text input fields support **keyboard shortcut Enter** to submit, reducing reliance on mouse clicks.
- Destructive actions (Delete File, Clear Tasks) trigger a **confirmation dialog** before execution.
- Sliders for Volume and Brightness show **current value labels** that update in real time.
- The reminder panel uses a **spinner widget** for minute selection, not a free-text field.
- All buttons are **disabled** (grayed out) when their prerequisite is unmet (e.g., Read File button disabled when no filename is entered).
- A **command history panel** (scrollable, last 200 entries) is always visible, matching the voice interface's spoken feedback trail.

---

## 🧠 Nielsen's 10 Usability Heuristics — Compliance Matrix

Both interfaces were designed from the ground up against all 10 Nielsen heuristics. The table below documents how each heuristic is implemented per interface.

| # | Heuristic | Voice Interface Implementation | GUI Interface Implementation |
|---|---|---|---|
| 1 | **Visibility of System Status** | TTS confirms every action immediately ("Done. File created."). Listening/Processing/Speaking states announced verbally. | Status badge in header updates in real time (🟢 Ready / 🔄 Processing / ✅ Done / ❌ Error). Response panel shows timestamped output for every action. Live system stats in status bar. |
| 2 | **Match Between System and the Real World** | Commands use natural everyday language ("Open calculator", "Remind me to drink water in 10 minutes"). No technical jargon required. | Button labels use plain action verbs ("Take Photo", "Add Task", "Clear Tasks"). Icons reinforce meaning. Input placeholders show realistic examples ("e.g. report.txt"). |
| 3 | **User Control and Freedom** | `"Stop"` / `"Cancel"` / `"Never mind"` intents abort the current action at any stage. `"Undo last"` reverses reversible actions. | Cancel/Undo buttons visible adjacent to every action button. Confirmation dialogs for destructive actions. Escape key dismisses any modal. |
| 4 | **Consistency and Standards** | All responses follow a uniform template: action confirmation + result + next-step hint. Verb-noun command structure is consistent across all 35+ intents. | Uniform button sizing, color coding by domain (blue = info, green = action, red = destructive), and consistent layout across all sidebar panels. Keyboard shortcuts follow OS conventions (Enter = confirm, Esc = cancel). |
| 5 | **Error Prevention** | High-confidence threshold for STT before execution. Ambiguous commands prompt clarification ("Did you mean X or Y?") rather than guessing. | Input validation before submission (empty fields blocked, invalid expressions flagged inline). Destructive actions require explicit confirmation. Disable-state buttons prevent impossible actions. |
| 6 | **Recognition Rather Than Recall** | `"Help"` intent reads all available commands for the current domain. `"What can you do?"` lists all capabilities. | All available actions are visible as labeled buttons at all times. No command memorization required. Tooltips on hover explain each control. |
| 7 | **Flexibility and Efficiency of Use** | Power users can chain commands naturally in speech. Wake word can be disabled for continuous-listen mode. Config exposes ENERGY_THRESHOLD and PAUSE_THRESHOLD for expert tuning. | Keyboard shortcuts for every frequent action. Enter submits any form. Sidebar tab keyboard navigation (Alt+1 through Alt+6). Expert users can bypass confirmation dialogs via a preferences toggle. |
| 8 | **Aesthetic and Minimalist Design** | TTS responses capped at ~50 words. No unnecessary filler phrases. Direct, informative responses only. | Clean layout with generous whitespace. Only the active domain's controls are shown in the main panel. No decorative clutter. Status bar shows only actionable metrics. |
| 9 | **Help Users Recognize, Diagnose, and Recover from Errors** | All errors are spoken in plain language ("I couldn't find that file. Try saying the full name."). Never speaks a raw exception. | Error messages appear inline in the Response Panel in red, with a plain-language explanation and a suggested fix. No raw tracebacks exposed to users. |
| 10 | **Help and Documentation** | `"Help"` intent available at any time; domain-specific help reads relevant commands. `"Tutorial"` intent walks through a guided 5-minute onboarding sequence. | Persistent `?` help button per panel opens a context-sensitive help popover. A `Getting Started` guided tour runs on first launch. Full command reference accessible via Help menu. |

---

## 📐 Architecture

VoiceAssist uses a **shared core** architecture. Both interfaces are thin modality-specific layers on top of the same task execution engine.

```
┌──────────────────────────┐     ┌──────────────────────────┐
│    VOICE INTERFACE        │     │      GUI INTERFACE        │
│  voice_interface.py       │     │   gui_interface.py        │
│                           │     │                           │
│  Mic → STT → IntentEngine │     │  tkinter widgets → action │
│  → core dispatch → TTS    │     │  → core dispatch → panel  │
└────────────┬─────────────┘     └────────────┬─────────────┘
             │                                │
             └──────────────┬─────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │      CORE ENGINE           │
              │  core/ — 7 domain modules  │
              │  (identical for both UIs)  │
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────┐
              │    RESEARCH LAYER          │
              │  metrics_logger.py         │
              │  nasa_tlx.py               │
              │  sus_survey.py             │
              │  session_manager.py        │
              └────────────────────────────┘
```

**Critical constraint:** The core modules must never be modified to accommodate either interface. All interface-specific adaptations live in `voice_interface.py` and `gui_interface.py` exclusively. This guarantees that any observed performance differences in user studies are attributable to the interaction modality, not implementation inconsistency.

---

## 🔬 Research Methodology

### Study Design

- **Design:** Within-subjects, counterbalanced (half participants: Voice first → GUI second; half: GUI first → Voice second)
- **Tasks:** Standardized 10-task battery covering all 7 domains, identical for both interfaces
- **Metrics collected per task:** Completion time (ms), error count, number of interactions required
- **Post-session measures:** NASA-TLX (cognitive load), SUS (usability), open-ended preference interview

### Metrics Logger

`metrics_logger.py` automatically captures:

```python
{
  "participant_id": "P01",
  "interface": "voice" | "gui",
  "session_order": 1 | 2,
  "task_id": "T03",
  "domain": "file_management",
  "start_time_ms": 1712000000000,
  "end_time_ms": 1712000005432,
  "duration_ms": 5432,
  "errors": 0,
  "interactions": 1,
  "completed": true
}
```

Logs are written to `data/research_logs/` as per-participant CSVs, ready for import into R or Python for statistical analysis (paired t-test / Wilcoxon signed-rank).

### Running a Study Session

```bash
# Start a counterbalanced study session for participant P01
python main.py --mode study --participant P01

# System automatically:
# 1. Determines interface order based on participant ID parity
# 2. Runs interface A with task battery + metrics logging
# 3. Prompts for NASA-TLX + SUS after session A
# 4. Switches to interface B
# 5. Repeats task battery + metrics logging
# 6. Prompts for NASA-TLX + SUS after session B
# 7. Exports participant CSV to data/research_logs/P01.csv
```

---

## 📦 Dependencies

```
SpeechRecognition           # Microphone input & Google Speech-to-Text
pyttsx3                     # Offline TTS
psutil                      # System resource monitoring
opencv-python               # Webcam capture
pytesseract                 # OCR
pyautogui                   # Screen capture
requests                    # Weather API
wikipedia                   # Wikipedia summaries
screen-brightness-control   # Cross-platform brightness
pycaw                       # Windows audio (Windows only)
tkinter                     # GUI (bundled with Python)
```

Install all at once:

```bash
pip install SpeechRecognition pyttsx3 psutil opencv-python pytesseract pyautogui requests wikipedia screen-brightness-control pycaw
```

---

## 🎤 Voice Command Reference

### 🌐 Information

| Say | Action |
|---|---|
| `"What time is it"` / `"Current time"` | Current time |
| `"What's the date"` / `"Today's date"` | Current date |
| `"Weather"` / `"Weather in [city]"` | OpenWeatherMap forecast |
| `"Search for [query]"` / `"Google [query]"` | Opens browser |
| `"Wikipedia [topic]"` / `"Tell me about [topic]"` | 2-sentence summary |

### 🖥️ System Control

| Say | Action |
|---|---|
| `"Volume up/down"` / `"Mute"` | Audio control |
| `"Brightness up/down"` | Screen brightness |
| `"Open [app]"` / `"Launch [app]"` | Launch application |
| `"Close [app]"` / `"Terminate [app]"` | Kill application |

### 📁 File Management

| Say | Action |
|---|---|
| `"Create file [name]"` | New .txt file in home dir |
| `"Read file [name]"` | Speaks first 500 chars |
| `"Delete file [name]"` | Deletes file |
| `"List files"` | Lists up to 10 files |
| `"Create folder [name]"` | New folder in home dir |

### ✅ Productivity

| Say | Action |
|---|---|
| `"Calculate [expression]"` | Arithmetic evaluation |
| `"Add task [task]"` | Appends to persistent to-do list |
| `"Show tasks"` / `"List to-dos"` | Reads to-do list |
| `"Clear tasks"` | Clears all tasks (with confirmation) |
| `"Remind me to [task] in [N] minutes"` | Threaded spoken reminder |

### 📷 Camera & Screen

| Say | Action |
|---|---|
| `"Take a photo"` | Webcam JPEG capture |
| `"Take screenshot"` | Timestamped PNG |
| `"Read screen"` / `"OCR screenshot"` | OCR + speaks text |

### 📊 System Monitoring

| Say | Action |
|---|---|
| `"CPU usage"` | Reports CPU % |
| `"RAM usage"` | Reports RAM usage |
| `"Disk usage"` | Reports disk usage |
| `"Open task manager"` | Launches OS task manager |

### 🆘 Meta / Help

| Say | Action |
|---|---|
| `"Help"` | Reads domain-specific commands |
| `"What can you do?"` | Full capability summary |
| `"Tutorial"` | Guided onboarding walkthrough |
| `"Stop"` / `"Cancel"` / `"Never mind"` | Abort current action |
| `"Undo last"` | Reverse last reversible action |

---

## 🌍 Platform Support

| Feature | Windows | macOS | Linux |
|---|:---:|:---:|:---:|
| Speech Recognition | ✅ | ✅ | ✅ |
| Text-to-Speech | ✅ | ✅ | ✅ |
| GUI Interface | ✅ | ✅ | ✅ |
| Volume Control | ✅ (pycaw) | ✅ (AppleScript) | ✅ (ALSA/PulseAudio) |
| Brightness Control | ✅ | ✅ | ✅ |
| App Launch/Terminate | ✅ | ✅ | ✅ |
| File Operations | ✅ | ✅ | ✅ |
| Webcam / Screenshot | ✅ | ✅ | ✅ |
| OCR | ✅ | ✅ | ✅ |
| Research Logging | ✅ | ✅ | ✅ |

---

## 🔧 Configuration Reference

All parameters live in `config.py`:

| Parameter | Default | Description |
|---|---|---|
| `LANGUAGE` | `"en-IN"` | STT language code |
| `WAKE_WORD` | `"hey assist"` | Wake word; `None` to disable |
| `TTS_RATE` | `175` | TTS rate (wpm) |
| `TTS_VOLUME` | `0.9` | TTS volume (0.0–1.0) |
| `ENERGY_THRESHOLD` | `300` | Mic sensitivity |
| `PAUSE_THRESHOLD` | `0.8` | Silence to end phrase (s) |
| `PHRASE_TIME_LIMIT` | `10` | Max phrase duration (s) |
| `DEFAULT_CITY` | `"Mumbai"` | Default city for weather |
| `OPENWEATHERMAP_API_KEY` | `""` | Free API key |
| `TESSERACT_PATH` | — | Tesseract binary path (Windows) |
| `GUI_THEME` | `"light"` | `"light"` or `"dark"` |
| `GUI_FONT_SIZE` | `11` | Base font size (px) |
| `CONFIRM_DESTRUCTIVE` | `True` | Confirmation dialogs for delete/clear |
| `STUDY_MODE` | `False` | Enables research metrics logging |
| `LOG_LEVEL` | `"INFO"` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## 🚨 Troubleshooting

**Microphone not detected**
Check default input device in system settings. Raise `ENERGY_THRESHOLD` in noisy environments.

**Speech not recognized**
Ensure active internet connection (Google STT is online). Speak clearly within 10 seconds of the listening prompt.

**GUI window does not open**
Confirm `tkinter` is available: `python -c "import tkinter"`. On Linux, install with `sudo apt install python3-tk`.

**Weather not working**
Add a valid `OPENWEATHERMAP_API_KEY` in `config.py` (free tier sufficient).

**OCR returning garbled text**
Ensure Tesseract is installed and `TESSERACT_PATH` is correctly set (Windows). OCR output is truncated to 300 characters for TTS.

**Volume control not working on Linux**
Install: `sudo apt install alsa-utils` or `pulseaudio-utils`.

**Brightness control not working**
On Linux, `screen-brightness-control` may need root or `udev` rules. See [library docs](https://github.com/Crozzers/screen-brightness-control).

---

## 📄 License

MIT License. See `LICENSE` for details.

---

## 🙏 Acknowledgements

Built as a course project for **Human-Computer Interaction (HCI)**.
Grounded in HCI research by Nielsen, Shneiderman, Sweller, Nass, and Norman.
Speech recognition via [Google Speech Recognition](https://cloud.google.com/speech-to-text).
Weather data from [OpenWeatherMap](https://openweathermap.org).
