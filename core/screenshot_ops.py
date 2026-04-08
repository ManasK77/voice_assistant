# core/screenshot_ops.py
"""
Screenshot operations — screen capture and OCR text extraction.
"""

import datetime
import logging
import os
import platform

import pyautogui
import pytesseract
from PIL import Image

from config import SCREENSHOTS_DIR

logger = logging.getLogger("VoiceAssist.ScreenshotOps")

# Configure Tesseract path on Windows
if platform.system() == "Windows":
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.isfile(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path


def take_screenshot(filename: str = None) -> str:
    """Take a screenshot and save it."""
    try:
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"

        screenshot = pyautogui.screenshot()
        save_path = os.path.join(SCREENSHOTS_DIR, filename)
        screenshot.save(save_path)

        return f"Screenshot saved as {filename}"

    except Exception as e:
        logger.error(f"Screenshot error: {e}", exc_info=True)
        return "Sorry, could not take a screenshot"


def read_screen_text() -> str:
    """Take a screenshot and extract text using OCR."""
    try:
        screenshot = pyautogui.screenshot()
        text = pytesseract.image_to_string(screenshot)
        text = text.strip()

        if not text:
            return "Could not read any text from the screen"

        # Truncate for TTS
        if len(text) > 300:
            text = text[:300] + "..."

        return f"The screen shows: {text}"

    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        return "Sorry, could not read text from the screen. Make sure Tesseract OCR is installed"
