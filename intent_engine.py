# intent_engine.py
"""
IntentEngine — Keyword-based intent detection and command routing.
"""

import logging

logger = logging.getLogger("VoiceAssist.IntentEngine")

# Structure: each entry maps to a module and action
INTENT_MAP = {
    "time":           {"keywords": ["time", "what time", "current time"],                        "module": "info",        "action": "get_time"},
    "date":           {"keywords": ["date", "today's date", "what day"],                         "module": "info",        "action": "get_date"},
    "weather":        {"keywords": ["weather", "temperature", "forecast", "how hot"],            "module": "info",        "action": "get_weather"},
    "search":         {"keywords": ["search for", "search", "look up", "who is", "what is", "tell me about", "what"],  "module": "info",  "action": "web_search"},
    "volume_up":      {"keywords": ["volume up", "increase volume", "louder"],                   "module": "system",      "action": "volume_up"},
    "volume_down":    {"keywords": ["volume down", "decrease volume", "quieter"],                "module": "system",      "action": "volume_down"},
    "mute":           {"keywords": ["mute", "silence", "quiet"],                                 "module": "system",      "action": "mute"},
    "brightness_up":  {"keywords": ["brightness up", "brighter", "increase brightness"],         "module": "system",      "action": "brightness_up"},
    "brightness_down":{"keywords": ["brightness down", "dimmer", "decrease brightness"],         "module": "system",      "action": "brightness_down"},
    "open_app":       {"keywords": ["open", "launch", "start"],                                  "module": "system",      "action": "open_app"},
    "close_app":      {"keywords": ["close", "kill", "exit", "terminate"],                       "module": "system",      "action": "close_app"},
    "create_file":    {"keywords": ["create file", "make file", "new file"],                     "module": "file",        "action": "create_file"},
    "read_file":      {"keywords": ["read file", "open file", "show file"],                      "module": "file",        "action": "read_file"},
    "delete_file":    {"keywords": ["delete file", "remove file"],                               "module": "file",        "action": "delete_file"},
    "list_files":     {"keywords": ["list files", "show files", "what files"],                   "module": "file",        "action": "list_files"},
    "create_folder":  {"keywords": ["create folder", "make folder", "new folder"],               "module": "file",        "action": "create_folder"},
    "take_photo":     {"keywords": ["take photo", "take a photo", "capture photo", "capture a photo", "take picture", "take a picture", "selfie"],    "module": "camera",      "action": "capture_photo"},
    "screenshot":     {"keywords": ["screenshot", "capture screen", "screen capture"],           "module": "screenshot",  "action": "take_screenshot"},
    "read_screen":    {"keywords": ["read screen", "what's on screen", "ocr"],                   "module": "screenshot",  "action": "read_screen_text"},
    "cpu":            {"keywords": ["cpu", "processor usage", "cpu usage"],                      "module": "status",      "action": "cpu_usage"},
    "ram":            {"keywords": ["ram", "memory usage", "ram usage"],                         "module": "status",      "action": "ram_usage"},
    "disk":           {"keywords": ["disk", "storage", "disk usage"],                            "module": "status",      "action": "disk_usage"},
    "system_status":  {"keywords": ["system status", "performance", "how is my computer"],       "module": "status",      "action": "full_status"},
    "task_manager":   {"keywords": ["task manager", "open task manager"],                        "module": "status",      "action": "open_task_manager"},
    "calculate":      {"keywords": ["calculate", "compute", "evaluate"],                         "module": "productivity","action": "calculate"},
    "add_todo":       {"keywords": ["add task", "add to-do", "remember to", "add todo"],         "module": "productivity","action": "add_todo"},
    "show_todos":     {"keywords": ["show tasks", "my tasks", "to-do list", "what are my tasks"],"module": "productivity","action": "show_todos"},
    "clear_todos":    {"keywords": ["clear tasks", "delete all tasks"],                          "module": "productivity","action": "clear_todos"},
    "set_reminder":   {"keywords": ["remind me", "set reminder", "set an alarm"],                "module": "productivity","action": "set_reminder"},
    "stop":           {"keywords": ["stop", "quit", "goodbye", "exit", "bye"],                   "module": "core",        "action": "stop"},
}


class IntentEngine:
    def detect(self, text: str) -> dict:
        """
        Detect intent from text using keyword matching.
        Returns dict with module, action, and raw_text.
        """
        text_lower = text.lower()

        # Sort by keyword length descending to match longer/more specific phrases first
        sorted_intents = sorted(
            INTENT_MAP.items(),
            key=lambda item: max(len(kw) for kw in item[1]["keywords"]),
            reverse=True,
        )

        for intent_name, intent_data in sorted_intents:
            for keyword in sorted(intent_data["keywords"], key=len, reverse=True):
                if keyword in text_lower:
                    logger.info(f"Detected intent: {intent_name} (keyword={keyword!r})")
                    return {
                        "module": intent_data["module"],
                        "action": intent_data["action"],
                        "raw_text": text,
                    }

        logger.info(f"No intent matched for: {text!r}")
        return {"module": "unknown", "action": "unknown", "raw_text": text}

    def extract_arg(self, text: str, keywords: list | str) -> str:
        """
        Strip matched keyword(s) from text and return the remainder as argument.
        """
        if isinstance(keywords, str):
            keywords = [keywords]

        text_lower = text.lower()

        # Sort keywords by length descending to strip the most specific first
        for keyword in sorted(keywords, key=len, reverse=True):
            if keyword in text_lower:
                idx = text_lower.index(keyword)
                result = text[:idx] + text[idx + len(keyword):]
                result = result.strip()
                if result:
                    return result

        return text.strip()
