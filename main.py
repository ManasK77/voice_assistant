# main.py
"""
VoiceAssist — Main Entry Point

Starts the voice interface, GUI interface, or both.
Usage:
    python main.py              # Voice mode (default)
    python main.py --mode gui   # GUI mode
    python main.py --mode both  # Both simultaneously
"""

import argparse
import logging
import sys
import threading
from logging.handlers import RotatingFileHandler

import config
from voice_io import VoiceIO
from intent_engine import IntentEngine
from core import info_ops, system_ops, file_ops, camera_skill, screenshot_ops, system_status, productivity

# --- Logging Setup ---
logger = logging.getLogger("VoiceAssist")
logger.setLevel(getattr(logging, config.LOG_LEVEL, logging.INFO))

log_file = config.LOGS_DIR + "/assistant.log"
file_handler = RotatingFileHandler(
    log_file,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT,
)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(name)s] %(levelname)s: %(message)s")
)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(
    logging.Formatter("[%(name)s] %(levelname)s: %(message)s")
)
logger.addHandler(console_handler)

# Global intent engine instance (used in route_command)
intent_engine = IntentEngine()


# --- Module Router ---
def route_command(intent: dict, voice: VoiceIO) -> None:
    """Route a detected intent to the appropriate module function."""
    module = intent["module"]
    action = intent["action"]
    raw = intent["raw_text"]
    response = None

    try:
        if module == "core" and action == "stop":
            voice.speak("Goodbye!")
            raise SystemExit

        elif module == "info":
            if action == "get_time":
                response = info_ops.get_time()
            elif action == "get_date":
                response = info_ops.get_date()
            elif action == "get_weather":
                response = info_ops.get_weather()
            elif action == "web_search":
                query = intent_engine.extract_arg(raw, ["search for", "search", "look up", "tell me about", "who is", "what is", "what"])
                response = info_ops.web_search(query)

        elif module == "system":
            if action == "volume_up":
                response = system_ops.volume_up()
            elif action == "volume_down":
                response = system_ops.volume_down()
            elif action == "mute":
                response = system_ops.mute()
            elif action == "brightness_up":
                response = system_ops.brightness_up()
            elif action == "brightness_down":
                response = system_ops.brightness_down()
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
            elif action == "list_files":
                response = file_ops.list_files()
            elif action == "create_folder":
                name = intent_engine.extract_arg(raw, ["create folder", "make folder", "new folder"])
                response = file_ops.create_folder(name)

        elif module == "camera":
            if action == "capture_photo":
                response = camera_skill.capture_photo()

        elif module == "screenshot":
            if action == "take_screenshot":
                response = screenshot_ops.take_screenshot()
            elif action == "read_screen_text":
                response = screenshot_ops.read_screen_text()

        elif module == "status":
            if action == "cpu_usage":
                response = system_status.cpu_usage()
            elif action == "ram_usage":
                response = system_status.ram_usage()
            elif action == "disk_usage":
                response = system_status.disk_usage()
            elif action == "full_status":
                response = system_status.full_status()
            elif action == "open_task_manager":
                response = system_status.open_task_manager()

        elif module == "productivity":
            if action == "calculate":
                expr = intent_engine.extract_arg(raw, ["calculate", "what is", "compute"])
                response = productivity.calculate(expr)
            elif action == "add_todo":
                task = intent_engine.extract_arg(raw, ["add task", "add to-do", "remember to", "add todo"])
                response = productivity.add_todo(task)
            elif action == "show_todos":
                response = productivity.show_todos()
            elif action == "clear_todos":
                response = productivity.clear_todos()
            elif action == "set_reminder":
                response = productivity.set_reminder(raw, speak_fn=voice.speak)

        else:
            response = "I didn't understand that command. Please try again."

        if response:
            voice.speak(response)
            logger.info(f"CMD: {raw!r} -> {module}.{action} -> {response!r}")

    except SystemExit:
        raise
    except Exception as e:
        logger.error(f"Error routing command: {e}", exc_info=True)
        voice.speak("Something went wrong. Please try again.")


# --- Voice Loop ---
def voice_loop(voice: VoiceIO):
    """Continuous voice listening loop."""
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
            intent = intent_engine.detect(text)
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


# --- CLI Argument Parsing ---
def parse_args():
    parser = argparse.ArgumentParser(
        description="VoiceAssist — Voice Assistant System",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--mode",
        choices=["voice", "gui", "both"],
        default="voice",
        help=(
            "Interface mode:\n"
            "  voice  — Voice-only interface (default)\n"
            "  gui    — GUI-only interface\n"
            "  both   — GUI + voice running simultaneously"
        ),
    )
    return parser.parse_args()


# --- Main Entry Point ---
def main():
    args = parse_args()

    if args.mode == "voice":
        # Original voice-only mode
        voice = VoiceIO()
        voice_loop(voice)

    elif args.mode == "gui":
        # GUI-only mode — no microphone needed
        from interfaces.gui_interface import GUIInterface
        gui = GUIInterface()
        gui.run()

    elif args.mode == "both":
        # GUI on main thread + voice loop on background thread
        from interfaces.gui_interface import GUIInterface

        voice = VoiceIO()
        gui = GUIInterface()

        # Wire voice events to GUI log
        original_speak = voice.speak

        def speak_with_gui(text):
            original_speak(text)
            gui.log_external(f"[ASSISTANT] {text}", "info")

        voice.speak = speak_with_gui

        # Start voice loop in background
        voice_thread = threading.Thread(target=voice_loop, args=(voice,), daemon=True)
        voice_thread.start()

        gui.run()


if __name__ == "__main__":
    main()
