# core/system_ops.py
"""
System operations — volume, brightness, open/close applications.
Platform-aware: Windows, macOS, Linux.
"""

import logging
import os
import platform
import subprocess

import psutil

logger = logging.getLogger("VoiceAssist.SystemOps")

PLATFORM = platform.system()  # "Windows", "Darwin", "Linux"

# Conditionally import Windows volume control
if PLATFORM == "Windows":
    try:
        from ctypes import cast, POINTER
        from comtypes import CLSCTX_ALL
        from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
        PYCAW_AVAILABLE = True
    except ImportError:
        PYCAW_AVAILABLE = False
        logger.warning("pycaw not available — volume control may not work")
else:
    PYCAW_AVAILABLE = False


def _get_volume_interface():
    """Get the Windows audio endpoint volume interface via pycaw."""
    speakers = AudioUtilities.GetSpeakers()
    # Newer pycaw versions return an AudioDevice wrapper with EndpointVolume
    if hasattr(speakers, 'EndpointVolume'):
        return speakers.EndpointVolume
    # Fallback for older pycaw versions using raw COM device
    interface = speakers.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    return cast(interface, POINTER(IAudioEndpointVolume))


def volume_up(step: int = 10) -> str:
    """Increase system volume."""
    try:
        if PLATFORM == "Windows" and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            current = volume.GetMasterVolumeLevelScalar()
            new_level = min(current + step / 100.0, 1.0)
            volume.SetMasterVolumeLevelScalar(new_level, None)
        elif PLATFORM == "Darwin":
            subprocess.run(
                ["osascript", "-e",
                 f"set volume output volume (output volume of (get volume settings) + {step})"],
                check=True,
            )
        elif PLATFORM == "Linux":
            subprocess.run(
                ["amixer", "-D", "pulse", "sset", "Master", f"{step}%+"],
                check=True,
            )
        return "Done. Volume has been increased successfully."
    except Exception as e:
        logger.error(f"Volume up error: {e}", exc_info=True)
        return "Could not increase volume"


def volume_down(step: int = 10) -> str:
    """Decrease system volume."""
    try:
        if PLATFORM == "Windows" and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            current = volume.GetMasterVolumeLevelScalar()
            new_level = max(current - step / 100.0, 0.0)
            volume.SetMasterVolumeLevelScalar(new_level, None)
        elif PLATFORM == "Darwin":
            subprocess.run(
                ["osascript", "-e",
                 f"set volume output volume (output volume of (get volume settings) - {step})"],
                check=True,
            )
        elif PLATFORM == "Linux":
            subprocess.run(
                ["amixer", "-D", "pulse", "sset", "Master", f"{step}%-"],
                check=True,
            )
        return "Done. Volume has been decreased successfully."
    except Exception as e:
        logger.error(f"Volume down error: {e}", exc_info=True)
        return "Could not decrease volume"


def mute() -> str:
    """Toggle system mute."""
    try:
        if PLATFORM == "Windows" and PYCAW_AVAILABLE:
            volume = _get_volume_interface()
            current_mute = volume.GetMute()
            volume.SetMute(not current_mute, None)
        elif PLATFORM == "Darwin":
            subprocess.run(
                ["osascript", "-e", "set volume with output muted"],
                check=True,
            )
        elif PLATFORM == "Linux":
            subprocess.run(
                ["amixer", "-D", "pulse", "sset", "Master", "toggle"],
                check=True,
            )
        return "Done. System has been muted successfully."
    except Exception as e:
        logger.error(f"Mute error: {e}", exc_info=True)
        return "Could not toggle mute"


def brightness_up(step: int = 10) -> str:
    """Increase screen brightness."""
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness()
        if isinstance(current, list):
            current = current[0]
        new_level = min(current + step, 100)
        sbc.set_brightness(new_level)
        return f"Done. Brightness increased to {new_level}% successfully."
    except Exception as e:
        logger.warning(f"Brightness up error: {e}")
        return "Could not increase brightness"


def brightness_down(step: int = 10) -> str:
    """Decrease screen brightness."""
    try:
        import screen_brightness_control as sbc

        current = sbc.get_brightness()
        if isinstance(current, list):
            current = current[0]
        new_level = max(current - step, 0)
        sbc.set_brightness(new_level)
        return f"Done. Brightness decreased to {new_level}% successfully."
    except Exception as e:
        logger.warning(f"Brightness down error: {e}")
        return "Could not decrease brightness"


# App name → platform-specific launch command
APP_MAP = {
    "calculator":   {"Windows": "calc",       "Darwin": "Calculator",       "Linux": "gnome-calculator"},
    "notepad":      {"Windows": "notepad",     "Darwin": "TextEdit",         "Linux": "gedit"},
    "browser":      {"Windows": "start chrome","Darwin": "Google Chrome",    "Linux": "google-chrome"},
    "chrome":       {"Windows": "start chrome","Darwin": "Google Chrome",    "Linux": "google-chrome"},
    "file manager": {"Windows": "explorer",    "Darwin": "Finder",           "Linux": "nautilus"},
    "explorer":     {"Windows": "explorer",    "Darwin": "Finder",           "Linux": "nautilus"},
    "terminal":     {"Windows": "cmd",         "Darwin": "Terminal",         "Linux": "gnome-terminal"},
    "paint":        {"Windows": "mspaint",     "Darwin": "Preview",          "Linux": "gimp"},
    "word":         {"Windows": "winword",     "Darwin": "Microsoft Word",   "Linux": "libreoffice --writer"},
    "excel":        {"Windows": "excel",       "Darwin": "Microsoft Excel",  "Linux": "libreoffice --calc"},
    "camera":       {"Windows": "start microsoft.windows.camera:", "Darwin": "Photo Booth", "Linux": "cheese"},
    "settings":     {"Windows": "start ms-settings:", "Darwin": "System Preferences", "Linux": "gnome-control-center"},
    "store":        {"Windows": "start ms-windows-store:", "Darwin": "App Store", "Linux": "gnome-software"},
    "clock":        {"Windows": "start ms-clock:", "Darwin": "Clock", "Linux": "gnome-clocks"},
}


# Known websites — spoken name -> URL
WEBSITE_MAP = {
    "youtube":    "https://www.youtube.com",
    "google":     "https://www.google.com",
    "gmail":      "https://mail.google.com",
    "facebook":   "https://www.facebook.com",
    "instagram":  "https://www.instagram.com",
    "twitter":    "https://www.twitter.com",
    "reddit":     "https://www.reddit.com",
    "amazon":     "https://www.amazon.com",
    "github":     "https://www.github.com",
    "linkedin":   "https://www.linkedin.com",
    "whatsapp":   "https://web.whatsapp.com",
    "netflix":    "https://www.netflix.com",
    "spotify":    "https://www.spotify.com",
    "chatgpt":    "https://chat.openai.com",
    "stackoverflow": "https://stackoverflow.com",
}


def _is_website(name: str) -> bool:
    """Check if the name looks like a website."""
    name_lower = name.lower().strip()
    if name_lower in WEBSITE_MAP:
        return True
    # Check for domain-like patterns (.com, .org, .in, .net, etc.)
    if any(name_lower.endswith(ext) for ext in [".com", ".org", ".net", ".in", ".io", ".co", ".edu", ".gov"]):
        return True
    return False


def open_app(app_name: str) -> str:
    """Open an application or website by name."""
    try:
        import webbrowser

        app_name_lower = app_name.lower().strip()

        # --- Check if it's a website first ---
        if app_name_lower in WEBSITE_MAP:
            url = WEBSITE_MAP[app_name_lower]
            webbrowser.open(url)
            return f"Done. {app_name} has been opened in Chrome successfully."

        # Check if it looks like a URL
        if _is_website(app_name_lower):
            url = app_name_lower if app_name_lower.startswith("http") else f"https://www.{app_name_lower}"
            webbrowser.open(url)
            return f"Done. {app_name} has been opened in Chrome successfully."

        # --- Otherwise try as a desktop app ---
        matched_key = None
        for key in APP_MAP:
            if key in app_name_lower or app_name_lower in key:
                matched_key = key
                break

        if matched_key and PLATFORM in APP_MAP[matched_key]:
            command = APP_MAP[matched_key][PLATFORM]
        else:
            command = app_name_lower

        if PLATFORM == "Windows":
            if command.startswith("start "):
                os.system(command)
            else:
                try:
                    os.startfile(command)
                except OSError:
                    subprocess.Popen(command, shell=True)
        elif PLATFORM == "Darwin":
            subprocess.Popen(["open", "-a", command])
        else:
            subprocess.Popen(command.split())

        return f"Done. {app_name} has been opened successfully."

    except Exception as e:
        logger.error(f"Open app error: {e}", exc_info=True)
        return f"Could not find or open {app_name}"


def close_app(app_name: str) -> str:
    """Close an application by killing its process."""
    try:
        app_name_lower = app_name.lower().strip()
        killed = False

        for proc in psutil.process_iter(["name"]):
            try:
                proc_name = proc.info["name"]
                if proc_name and app_name_lower in proc_name.lower():
                    proc.kill()
                    killed = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        if killed:
            return f"Done. {app_name} has been closed successfully."
        else:
            return f"No running process found for {app_name}"

    except Exception as e:
        logger.error(f"Close app error: {e}", exc_info=True)
        return f"Could not close {app_name}"
