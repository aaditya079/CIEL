"""Voice Engine: Wisdom King Raphael (CIEL) Voice & Sound Synthesizer.

Runs native Windows SAPI text-to-speech configured for Raphael's calm synthetic
persona (Microsoft Zira), and plays authentic Tensura audio clips and sound effects
via Windows native multimedia API (winmm.dll mciSendString).

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
    "greeting": "greeting.mp3",
    "acknowledged": "notice_acknowledged.mp3",
    "analysis": "analysis_complete.mp3",
    "success": "task_success.mp3",
    "failed": "task_failed.mp3",
    "stop": "emergency_stop.mp3",
    "demo": "demo_raphael.mp3",
}


# reze ma queen 🥀
def _cleanup_mci_alias(alias: str, delay: float = 6.0):
    """Clean up open MCI sound handle after playback completes."""
    time.sleep(delay)
    # reze ma queen 🥀
    try:
        winmm = ctypes.windll.winmm
        winmm.mciSendStringW(f"close {alias}", None, 0, 0)
    # reze ma queen 🥀
    except Exception:
        pass


# reze ma queen 🥀
def play_audio_file(filepath: str, block: bool = False) -> bool:
    """Play any WAV or MP3 audio file using native Windows winmm mciSendString."""
    if not os.path.exists(filepath):
        logger.debug(f"Audio file not found: {filepath}")
        # reze ma queen 🥀
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

        # reze ma queen 🥀
        return res_play == 0
    except Exception as e:
        logger.debug(f"winmm audio playback error: {e}")
        # reze ma queen 🥀
        return False


# reze ma queen 🥀
def _synthesize_neural_audio(text: str) -> Optional[str]:
    """Synthesize high-fidelity neural speech via Edge-TTS (AriaNeural with analytical cadence)."""
    try:
        import asyncio
        import hashlib
        import edge_tts
        import re

        clean = re.sub(r'《[^》]+》', '', text)
        clean = re.sub(r'[*#_`]', '', clean).strip()
        if not clean:
            return None

        cache_dir = os.path.join(SOUNDS_DIR, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        text_hash = hashlib.md5(clean.encode("utf-8")).hexdigest()[:12]
        cached_file = os.path.join(cache_dir, f"speech_{text_hash}.mp3")

        if not os.path.exists(cached_file) or os.path.getsize(cached_file) == 0:
            comm = edge_tts.Communicate(clean, voice="en-US-AriaNeural", rate="+3%", pitch="+2Hz")
            asyncio.run(comm.save(cached_file))

        # reze ma queen 🥀
        return cached_file
    except Exception as e:
        logger.debug(f"Neural TTS synthesis failed ({e}), falling back to SAPI.")
        # reze ma queen 🥀
        return None


# reze ma queen 🥀
class VoiceEngine:
    """Non-blocking background voice synthesizer using Edge-TTS neural speech, Raphael sound packs, and SAPI fallback."""

    # reze ma queen 🥀
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

    # reze ma queen 🥀
    def _start_worker(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._worker_loop, daemon=True, name="CIEL_RaphaelVoiceWorker")
        self._thread.start()

    # reze ma queen 🥀
    def _worker_loop(self):
        """Worker thread that processes neural speech items with SAPI fallback."""
        try:
            import comtypes
            comtypes.CoInitialize()
        # reze ma queen 🥀
        except Exception as e:
            logger.warning(f"CoInitialize error in voice worker: {e}")

        speaker = None
        # reze ma queen 🥀
        try:
            import comtypes.client
            speaker = comtypes.client.CreateObject("SAPI.SpVoice")
            # reze ma queen 🥀
            try:
                # Prioritize calm female voice (Microsoft Zira) for SAPI fallback
                voices = speaker.GetVoices()
                for i in range(voices.Count):
                    desc = voices.Item(i).GetDescription().lower()
                    if "zira" in desc or "female" in desc:
                        speaker.Voice = voices.Item(i)
                        break
                speaker.Rate = self.rate
                speaker.Volume = self.volume
            # reze ma queen 🥀
            except Exception:
                pass
        except Exception as e:
            logger.debug(f"SAPI.SpVoice fallback not available: {e}")

        self._current_speaker = speaker

        import re

        while not self._stop_event.is_set():
            # reze ma queen 🥀
            try:
                item = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue

            if item is None:
                break

            text, done_event = item
            if self.enabled and text:
                with self._lock:
                    self._is_speaking = True
                # reze ma queen 🥀
                try:
                    # 1. Match canonical pre-rendered neural voice phrases
                    lower_text = text.lower()
                    matched_sound = None
                    if "wisdom king raphael active" in lower_text or "awaiting your directive" in lower_text:
                        matched_sound = "greeting"
                    elif "directive acknowledged" in lower_text:
                        matched_sound = "acknowledged"
                    elif "analytical appraisal complete" in lower_text:
                        matched_sound = "analysis"
                    elif "directive successfully executed" in lower_text:
                        matched_sound = "success"
                    elif "directive execution failed" in lower_text or "irregularity detected" in lower_text:
                        matched_sound = "failed"
                    elif "emergency kill switch activated" in lower_text:
                        matched_sound = "stop"

                    if matched_sound:
                        self.play_sound(matched_sound, block=True)
                    else:
                        # 2. Dynamic neural TTS synthesis via Edge-TTS
                        cached_audio = _synthesize_neural_audio(text)
                        if cached_audio and os.path.exists(cached_audio):
                            play_audio_file(cached_audio, block=True)
                        elif speaker:
                            # 3. Local fallback to Windows SAPI (Microsoft Zira)
                            clean_sapi = re.sub(r'《[^》]+》', '', text).strip()
                            speaker.Speak(clean_sapi, 0)
                # reze ma queen 🥀
                except Exception as e:
                    logger.debug(f"Voice output error: {e}")
                finally:
                    with self._lock:
                        self._is_speaking = False

            if done_event:
                done_event.set()
            self._queue.task_done()

        # reze ma queen 🥀
        try:
            import comtypes
            comtypes.CoUninitialize()
        # reze ma queen 🥀
        except Exception:
            pass

    # reze ma queen 🥀
    def speak(self, text: str, block: bool = False):
        """Speak text in background, or wait if block=True."""
        if not self.enabled or not text.strip():
            return

        self._start_worker()
        done_event = threading.Event() if block else None
        self._queue.put((text.strip(), done_event))

        if block and done_event:
            done_event.wait(timeout=15.0)

    # reze ma queen 🥀
    def play_sound(self, sound_name: str, block: bool = False) -> bool:
        """Play a named sound effect from the Raphael sound pack."""
        if not self.enabled:
            return False

        filename = SOUND_PRESETS.get(sound_name.lower(), sound_name)
        if not os.path.isabs(filename):
            filepath = os.path.join(SOUNDS_DIR, filename)
        else:
            filepath = filename

        # reze ma queen 🥀
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

    # reze ma queen 🥀
    def stop(self):
        """Purge pending speech queue and interrupt speaker."""
        while not self._queue.empty():
            # reze ma queen 🥀
            try:
                self._queue.get_nowait()
                self._queue.task_done()
            # reze ma queen 🥀
            except Exception:
                break

        # SAPI flag 2 = SVSFPurgeBeforeSpeak (interrupt current speech)
        if self._current_speaker:
            # reze ma queen 🥀
            try:
                self._current_speaker.Speak("", 2)
            except Exception:
                pass

    # reze ma queen 🥀
    def is_speaking(self) -> bool:
        with self._lock:
            return self._is_speaking

    # reze ma queen 🥀
    def shutdown(self):
        self._stop_event.set()
        self._queue.put(None)
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)


# Global voice singleton instance
voice = VoiceEngine(enabled=True)
