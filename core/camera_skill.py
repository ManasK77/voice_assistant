# core/camera_skill.py
"""
Camera operations — webcam capture and optional face detection.
"""

import datetime
import logging
import os

import cv2

from config import PHOTOS_DIR

logger = logging.getLogger("VoiceAssist.CameraSkill")


def capture_photo(filename: str = None) -> str:
    """Capture a photo from the default webcam."""
    try:
        if filename is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"photo_{timestamp}.jpg"

        cap = cv2.VideoCapture(0)

        if not cap.isOpened():
            return "No camera found"

        # Let the camera warm up
        for _ in range(5):
            cap.read()

        # Show preview window for 2 seconds
        ret, frame = cap.read()
        if not ret:
            cap.release()
            return "Could not capture photo from camera"

        cv2.imshow("VoiceAssist - Photo Preview", frame)
        cv2.waitKey(2000)

        # Save the frame
        save_path = os.path.join(PHOTOS_DIR, filename)
        cv2.imwrite(save_path, frame)

        cap.release()
        cv2.destroyAllWindows()

        return f"Photo saved as {filename}"

    except Exception as e:
        logger.error(f"Camera capture error: {e}", exc_info=True)
        try:
            cap.release()
            cv2.destroyAllWindows()
        except Exception:
            pass
        return "Sorry, something went wrong with the camera"


def detect_objects(image_path: str) -> str:
    """Detect faces in an image using Haar cascades."""
    try:
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

        image = cv2.imread(image_path)
        if image is None:
            return "Could not load the image"

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )

        count = len(faces)
        if count == 0:
            return "No faces detected"
        elif count == 1:
            return "Detected 1 face in the image"
        else:
            return f"Detected {count} faces in the image"

    except Exception as e:
        logger.error(f"Object detection error: {e}", exc_info=True)
        return "Sorry, something went wrong with face detection"
