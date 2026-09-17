"""Voice Engine: Native Windows SAPI text-to-speech running asynchronously."""

import threading
import queue
import logging
import time
from typing import Optional

logger = logging.getLogger("desktop_agent.computer.voice")

class VoiceEngine:
    """Non-blocking background voice synthesizer using Windows SAPI COM."""

    def __init__(self, enabled: bool = True, rate: int = 1, volume: int = 100):
        self.enabled = enabled
        self.rate = rate      # -10 to 10
        self.volume = volume  # 0 to 100
        self._queue: queue.Queue = queue.Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_speaker = None
        self._lock = threading.Lock()
        self._is_speaking = False

        if self.enabled:
            self._start_worker()

    def _start_worker(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="CIEL_VoiceWorker")
        self._thread.start()

    def _worker_loop(self):
        """Worker thread that initializes COM and processes speech items."""
        try:
            import comtypes
            comtypes.CoInitialize()
        except Exception as e:
            logger.warning(f"CoInitialize error in voice worker: {e}")

        speaker = None
        try:
            import comtypes.client
            speaker = comtypes.client.CreateObject("SAPI.SpVoice")
            try:
                speaker.Rate = self.rate
                speaker.Volume = self.volume
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Failed to create SAPI.SpVoice: {e}. Voice feedback disabled.")
            return

        self._current_speaker = speaker

        while not self._stop_event.is_set():
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if item is None:
                break

            text, done_event = item
            if self.enabled and text and speaker:
                with self._lock:
                    self._is_speaking = True
                try:
                    # SAPI Speech flags: 0 = synchronous within this worker thread
                    speaker.Speak(text, 0)
                except Exception as e:
                    logger.debug(f"SAPI Speak error: {e}")
                finally:
                    with self._lock:
                        self._is_speaking = False

            if done_event:
                done_event.set()
            self._queue.task_done()

        try:
            import comtypes
            comtypes.CoUninitialize()
        except Exception:
            pass

    def speak(self, text: str, block: bool = False):
        """Speak text in background, or wait if block=True."""
        if not self.enabled or not text.strip():
            return

        self._start_worker()
        done_event = threading.Event() if block else None
        self._queue.put((text.strip(), done_event))

        if block and done_event:
            done_event.wait(timeout=15.0)

    def stop(self):
        """Purge pending speech queue and interrupt speaker."""
        # Empty queue
        while not self._queue.empty():
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            except Exception:
                break

        # SAPI flag 2 = SVSFPurgeBeforeSpeak (interrupt current speech)
        if self._current_speaker:
            try:
                self._current_speaker.Speak("", 2)
            except Exception:
                pass

    def is_speaking(self) -> bool:
        with self._lock:
            return self._is_speaking

    def shutdown(self):
        self._stop_event.set()
        self._queue.put(None)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


# Global voice singleton instance
voice = VoiceEngine(enabled=True)
