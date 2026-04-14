# core/screenshot_ops.py
"""
Screenshot operations — screen capture and OCR text extraction.
"""

import datetime
import logging
import os
import platform
import shutil

import pyautogui
import pytesseract
from PIL import Image

from config import SCREENSHOTS_DIR

logger = logging.getLogger("VoiceAssist.ScreenshotOps")

# ---------------------------------------------------------------------------
# Robust Tesseract path detection (Windows)
# ---------------------------------------------------------------------------
_tesseract_available = False

def _find_tesseract() -> str | None:
    """Locate the Tesseract executable across common install locations."""
    # 1. Already in PATH?
    found = shutil.which("tesseract")
    if found:
        return found

    if platform.system() != "Windows":
        return None  # On Linux / macOS, rely on PATH

    # 2. Scan common Windows install directories
    candidate_dirs = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
        os.path.expandvars(r"%LOCALAPPDATA%\Tesseract-OCR"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR"),
        os.path.expandvars(r"%USERPROFILE%\AppData\Local\Tesseract-OCR"),
        # Chocolatey / Scoop
        r"C:\tools\Tesseract-OCR",
        os.path.expandvars(r"%USERPROFILE%\scoop\apps\tesseract\current"),
    ]

    for directory in candidate_dirs:
        exe = os.path.join(directory, "tesseract.exe")
        if os.path.isfile(exe):
            return exe

    return None


_tesseract_path = _find_tesseract()

if _tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = _tesseract_path
    _tesseract_available = True
    logger.info("Tesseract OCR found at: %s", _tesseract_path)
else:
    logger.warning(
        "Tesseract OCR was NOT found. 'Read screen' (OCR) will not work. "
        "Install from https://github.com/UB-Mannheim/tesseract/wiki and "
        "ensure tesseract.exe is on the system PATH or in a standard location."
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def take_screenshot(filename: str = None) -> str:
    """Take a screenshot and save it."""
    try:
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        screenshot = pyautogui.screenshot()
        save_path = os.path.join(SCREENSHOTS_DIR, filename)
        screenshot.save(save_path)

        return f"Done. Screenshot has been captured and saved as {filename} successfully."

    except Exception as e:
        logger.error(f"Screenshot error: {e}", exc_info=True)
        return "Sorry, could not take a screenshot"


def read_screen_text() -> str:
    """Take a screenshot and extract visible text using OCR (Tesseract)."""
    if not _tesseract_available:
        return (
            "OCR is not available. Please install Tesseract OCR: "
            "download from https://github.com/UB-Mannheim/tesseract/wiki, "
            "run the installer, and make sure to check 'Add to PATH' during setup. "
            "Then restart the assistant."
        )

    try:
        screenshot = pyautogui.screenshot()
        # Convert to RGB explicitly (pyautogui can return RGBA on some systems)
        screenshot = screenshot.convert("RGB")
        text = pytesseract.image_to_string(screenshot)
        text = text.strip()

        if not text:
            return "Could not read any text from the screen"

        # Truncate for TTS (300 chars ≈ 20 seconds of speech)
        if len(text) > 300:
            text = text[:300] + "..."

        logger.info("OCR extracted %d characters from screen", len(text))
        return f"The screen shows: {text}"

    except pytesseract.TesseractNotFoundError:
        logger.error("Tesseract binary not found despite earlier detection", exc_info=True)
        return (
            "Tesseract OCR was detected at startup but cannot be reached now. "
            "Please verify the installation and restart the assistant."
        )
    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        return "Sorry, something went wrong while reading the screen"
