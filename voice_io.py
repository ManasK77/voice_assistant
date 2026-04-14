# voice_io.py
"""
VoiceIO — Speech recognition and text-to-speech wrapper.
"""

import logging
import time
import speech_recognition as sr
import pyttsx3

import config

logger = logging.getLogger("VoiceAssist.VoiceIO")


class VoiceIO:
    def __init__(self):
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = config.SR_ENERGY_THRESHOLD
        self.recognizer.pause_threshold = config.SR_PAUSE_THRESHOLD

    def _create_engine(self):
        """Create a fresh pyttsx3 engine instance with configured settings.

        pyttsx3 on Windows (sapi5) has a known issue where runAndWait()
        can leave the engine loop in a broken state, causing subsequent
        speak calls to produce no audio. Creating a fresh engine for
        each call is the standard workaround.
        """
        engine = pyttsx3.init()
        engine.setProperty("rate", config.TTS_RATE)
        engine.setProperty("volume", config.TTS_VOLUME)
        voices = engine.getProperty("voices")
        if voices and config.TTS_VOICE_INDEX < len(voices):
            engine.setProperty("voice", voices[config.TTS_VOICE_INDEX].id)
        return engine

    def speak(self, text: str) -> None:
        """Speak the given text using TTS and print to console."""
        print(f"[ASSISTANT] {text}")
        logger.info(f"Speaking: {text}")

        try:
            engine = self._create_engine()
            engine.say(text)
            engine.runAndWait()
            engine.stop()
        except Exception as e:
            logger.warning(f"TTS error: {e}")
            # Last-resort fallback: try once more with a fresh engine
            try:
                engine = pyttsx3.init()
                engine.say(text)
                engine.runAndWait()
                engine.stop()
            except Exception as e2:
                logger.error(f"TTS fallback also failed: {e2}")

    def listen(self) -> str | None:
        """Listen for a voice command and return the recognized text."""
        try:
            with sr.Microphone() as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = self.recognizer.listen(
                    source,
                    timeout=config.SR_TIMEOUT,
                    phrase_time_limit=config.SR_PHRASE_LIMIT,
                )

            text = self.recognizer.recognize_google(audio, language=config.SR_LANGUAGE)
            text = text.lower().strip()
            print(f"[YOU] {text}")
            logger.info(f"Heard: {text!r}")

            return text

        except sr.WaitTimeoutError:
            return None
        except sr.UnknownValueError:
            return None
        except sr.RequestError as e:
            logger.warning(f"Speech service error: {e}")
            self.speak("Speech service unavailable.")
            return None
        except Exception as e:
            logger.error(f"Listen error: {e}", exc_info=True)
            return None

    def listen_continuous(self, callback: callable) -> None:
        """Continuously listen and call callback with recognized text."""
        while True:
            result = self.listen()
            if result is not None:
                callback(result)
            time.sleep(0.1)
