# voice_io.py
"""
VoiceIO — Speech recognition and text-to-speech wrapper.

Supports interruptible TTS: speech runs in a background thread so the
main voice-loop can keep listening for "stop" / "shut up" commands.
"""

import ctypes
import logging
import threading
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

        # TTS state
        self._tts_thread: threading.Thread | None = None
        self._tts_engine: pyttsx3.Engine | None = None
        self._tts_lock = threading.Lock()
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # TTS helpers
    # ------------------------------------------------------------------
    def _create_engine(self) -> pyttsx3.Engine:
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

    def _tts_worker(self, text: str) -> None:
        """Background worker that runs TTS to completion (or until stopped)."""
        try:
            engine = self._create_engine()
            with self._tts_lock:
                self._tts_engine = engine

            engine.say(text)
            engine.runAndWait()
        except RuntimeError:
            # engine.stop() was called from another thread — this is expected
            pass
        except Exception as e:
            logger.warning(f"TTS worker error: {e}")
        finally:
            with self._tts_lock:
                try:
                    if self._tts_engine is not None:
                        self._tts_engine.stop()
                except Exception:
                    pass
                self._tts_engine = None
            self._stop_event.clear()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def is_speaking(self) -> bool:
        """Return True if TTS is currently active."""
        return self._tts_thread is not None and self._tts_thread.is_alive()

    def speak(self, text: str, blocking: bool = True) -> None:
        """Speak the given text using TTS.

        Args:
            text: The text to speak.
            blocking: If True (default), wait for speech to finish.
                      If False, return immediately while speech plays
                      in the background (can be interrupted via stop_speaking).
        """
        print(f"[ASSISTANT] {text}")
        logger.info(f"Speaking: {text}")

        # If already speaking, stop the current utterance first
        if self.is_speaking:
            self.stop_speaking()

        self._stop_event.clear()
        self._tts_thread = threading.Thread(
            target=self._tts_worker, args=(text,), daemon=True,
        )
        self._tts_thread.start()

        if blocking:
            self._tts_thread.join()

    def stop_speaking(self) -> None:
        """Interrupt any current TTS playback immediately."""
        if not self.is_speaking:
            return

        logger.info("Stopping TTS playback")
        self._stop_event.set()

        with self._tts_lock:
            if self._tts_engine is not None:
                try:
                    self._tts_engine.stop()
                except Exception as e:
                    logger.debug(f"engine.stop() raised: {e}")

        # Give the thread a moment to exit cleanly
        if self._tts_thread is not None:
            self._tts_thread.join(timeout=1.0)

            # If the thread is still alive (pyttsx3+sapi5 can hang), force-kill it
            if self._tts_thread.is_alive():
                logger.warning("TTS thread did not exit cleanly; forcing termination")
                self._force_kill_thread(self._tts_thread)

        self._tts_thread = None
        with self._tts_lock:
            self._tts_engine = None

    @staticmethod
    def _force_kill_thread(thread: threading.Thread) -> None:
        """Last-resort: raise SystemExit in the target thread (Windows CPython)."""
        try:
            tid = thread.ident
            if tid is None:
                return
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_ulong(tid), ctypes.py_object(SystemExit),
            )
            if res == 0:
                logger.debug("Thread already exited")
            elif res > 1:
                # Something went wrong — revert
                ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_ulong(tid), None)
        except Exception as e:
            logger.debug(f"Force-kill failed: {e}")

    # ------------------------------------------------------------------
    # Listening
    # ------------------------------------------------------------------
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
