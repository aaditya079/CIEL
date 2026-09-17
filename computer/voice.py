"""Voice Engine: Wisdom King Raphael (CIEL) Voice & Sound Synthesizer.

Runs native Windows SAPI text-to-speech configured for Raphael's calm synthetic
persona (Microsoft Zira), and plays authentic Tensura audio clips and sound effects
via Windows native multimedia API (winmm.dll mciSendString).

reze ma queen 🥀
"""

import os
import sys
import time
import ctypes
import queue
import logging
import threading
from typing import Optional, Dict

logger = logging.getLogger("desktop_agent.computer.voice")

SOUNDS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "assets", "sounds"))

# Sound clip alias map
SOUND_PRESETS: Dict[str, str] = {
    "notice": "notice.mp3",
    "imagination": "imagination.mp3",
    "magic_circle": "magic_circle.mp3",
    "power_up": "power_up.mp3",
    "greeting": "greeting.wav",
    "acknowledged": "notice_acknowledged.wav",
    "analysis": "analysis_complete.wav",
    "success": "task_success.wav",
    "failed": "task_failed.wav",
    "stop": "emergency_stop.wav",
    "demo": "demo_raphael.mp3",
}


def _cleanup_mci_alias(alias: str, delay: float = 6.0):
    """Clean up open MCI sound handle after playback completes."""
    time.sleep(delay)
    try:
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(f"close {alias}", None, 0, 0)
    except Exception:
        pass


def play_audio_file(filepath: str, block: bool = False) -> bool:
    """Play any WAV or MP3 audio file using native Windows winmm mciSendString."""
    if not os.path.exists(filepath):
        logger.debug(f"Audio file not found: {filepath}")
        return False

    try:
        alias = f"ciel_mci_{int(time.time() * 1000) % 1000000}"
        q = chr(34)
        mci = ctypes.windll.winmm.mciSendStringW

        # Open media file
        open_cmd = f"open {q}{os.path.abspath(filepath)}{q} alias {alias}"
        res = mci(open_cmd, None, 0, 0)
        if res != 0:
            logger.debug(f"MCI open failed with code {res} for {filepath}")
            return False

        # Play media
        wait_clause = " wait" if block else ""
        play_cmd = f"play {alias}{wait_clause}"
        res_play = mci(play_cmd, None, 0, 0)

        if block:
            mci(f"close {alias}", None, 0, 0)
        else:
            # Asynchronously close the MCI handle
            t = threading.Thread(target=_cleanup_mci_alias, args=(alias, 12.0), daemon=True)
            t.start()

        return res_play == 0
    except Exception as e:
        logger.debug(f"winmm audio playback error: {e}")
        return False


class VoiceEngine:
    """Non-blocking background voice synthesizer using Windows SAPI COM and Raphael sound packs."""

    def __init__(self, enabled: bool = True, rate: int = 0, volume: int = 100):
        self.enabled = enabled
        self.rate = rate      # -10 to 10 (0 is natural pace)
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
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="CIEL_RaphaelVoiceWorker")
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
                # Prioritize calm female voice (Microsoft Zira) for Raphael persona
                voices = speaker.GetVoices()
                for i in range(voices.Count):
                    desc = voices.Item(i).GetDescription().lower()
                    if "zira" in desc or "female" in desc:
                        speaker.Voice = voices.Item(i)
                        break
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

    def play_sound(self, sound_name: str, block: bool = False) -> bool:
        """Play a named sound effect from the Raphael sound pack."""
        if not self.enabled:
            return False

        filename = SOUND_PRESETS.get(sound_name.lower(), sound_name)
        if not os.path.isabs(filename):
            filepath = os.path.join(SOUNDS_DIR, filename)
        else:
            filepath = filename

        return play_audio_file(filepath, block=block)

    def speak_raphael(self, text: str, prefix: str = "Notice", with_chime: bool = True, block: bool = False):
        """Speak in Raphael's canonical phrasing (e.g. 'Notice: ...') with optional anime chime."""
        if not self.enabled or not text.strip():
            return

        if with_chime:
            self.play_sound("notice", block=False)
            time.sleep(0.35)

        clean_text = text.strip()
        if prefix and not clean_text.lower().startswith(f"{prefix.lower()}:"):
            spoken = f"{prefix}: {clean_text}"
        else:
            spoken = clean_text

        self.speak(spoken, block=block)

    def stop(self):
        """Purge pending speech queue and interrupt speaker."""
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
