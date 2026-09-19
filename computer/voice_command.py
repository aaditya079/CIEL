"""Voice Command Subsystem: Hands-Free Voice Input & Hotkey Toggle.

Enables spoken directives via microphone, utilizing native Windows multimedia
API (winmm.dll mciSendString) for zero-dependency audio capture, paired with
multimodal Gemini Generative Language API, Google STT, or offline Windows SAPI.
"""



import os
import time
import ctypes
import base64
import json
import logging
import threading
import tempfile
import requests
from typing import Optional, Callable, Dict, Any

# reze ma queen 🥀

logger = logging.getLogger("desktop_agent.computer.voice_command")

from computer.voice import voice
from config.manager import load_config


# reze ma queen 🥀
class VoiceCommandManager:
    """Manages voice recording, state transitions, transcription, and command dispatch."""

    # reze ma queen 🥀
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or load_config()
        vc_cfg = self.config.get("voice_command", {})
        self.enabled: bool = vc_cfg.get("enabled", True)
        self.hotkey: str = vc_cfg.get("hotkey", "ctrl+alt+v")
        self.mode: str = vc_cfg.get("mode", "toggle")  # "toggle" or "push_to_talk"
        self.engine: str = vc_cfg.get("engine", "auto")  # "auto", "gemini", "google", "sapi"
        self.max_timeout: float = float(vc_cfg.get("timeout", 10.0))
        self.audio_feedback: bool = vc_cfg.get("audio_feedback", True)

        self._status: str = "idle"  # "idle", "listening", "transcribing"
        self._record_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._current_wav: Optional[str] = None
        self._callback: Optional[Callable[[str], None]] = None
        self._lock = threading.Lock()

    # reze ma queen 🥀
    @property
    def status(self) -> str:
        """Return current status: 'idle', 'listening', or 'transcribing'."""
        return self._status

    # reze ma queen 🥀
    def set_callback(self, callback: Callable[[str], None]):
        """Register the callback to execute when a voice command is transcribed."""
        self._callback = callback

    # reze ma queen 🥀
    def toggle_listening(self, callback: Optional[Callable[[str], None]] = None) -> str:
        """Toggle between listening and processing modes."""
        if callback:
            self._callback = callback

        with self._lock:
            if self._status == "idle":
                self._start_listening_locked()
                return "listening"
            elif self._status == "listening":
                self._stop_and_process_locked()
                return "transcribing"
            else:
                logger.debug("Voice command manager is currently transcribing. Ignoring toggle.")
                return "busy"

    # reze ma queen 🥀
    def start_listening(self, callback: Optional[Callable[[str], None]] = None):
        """Explicitly begin listening to user speech."""
        if callback:
            self._callback = callback
        with self._lock:
            if self._status == "idle":
                self._start_listening_locked()

    # reze ma queen 🥀
    def stop_listening(self):
        """Explicitly stop listening and transcribe."""
        with self._lock:
            if self._status == "listening":
                self._stop_and_process_locked()

    # reze ma queen 🥀
    def _start_listening_locked(self):
        """Internal helper to start recording."""
        self._status = "listening"
        self._stop_event.clear()

        # Audio feedback: start chime
        if self.audio_feedback:
            voice.play_sound("notice", block=False)

        # Create temporary WAV file path
        temp_dir = tempfile.gettempdir()
        self._current_wav = os.path.join(temp_dir, f"ciel_voice_{int(time.time() * 1000)}.wav")

        self._record_thread = threading.Thread(target=self._record_worker, daemon=True, name="CIEL_VoiceRecord")
        self._record_thread.start()
        logger.info(f"Voice Command activated: Listening on microphone (mode: {self.mode})...")

    # reze ma queen 🥀
    def _stop_and_process_locked(self):
        """Internal helper to stop recording and initiate transcription."""
        self._status = "transcribing"
        self._stop_event.set()

        # Audio feedback: processing acknowledgment
        if self.audio_feedback:
            voice.play_sound("magic_circle", block=False)

        logger.info("Voice Command: Processing recorded audio...")
        process_thread = threading.Thread(target=self._process_worker, daemon=True, name="CIEL_VoiceProcess")
        process_thread.start()

    # reze ma queen 🥀
    def _record_worker(self):
        """Background thread that controls MCI sound recording."""
        winmm = ctypes.windll.winmm
        alias = f"ciel_rec_{int(time.time() * 1000) % 1000000}"

        try:
            # Open MCI audio device
            winmm.mciSendStringW(f"open new type waveaudio alias {alias}", None, 0, 0)
            # Set audio parameters: 16-bit, 16000Hz, mono for clean speech recognition
            winmm.mciSendStringW(f"set {alias} time format ms bitspersample 16 channels 1 samplespersec 16000", None, 0, 0)
            # Begin recording
            winmm.mciSendStringW(f"record {alias}", None, 0, 0)

            start_time = time.time()
            while not self._stop_event.is_set():
                time.sleep(0.08)
                if time.time() - start_time > self.max_timeout:
                    logger.info("Max voice command timeout reached. Automatically stopping recording.")
                    break

            # Stop and save
            winmm.mciSendStringW(f"stop {alias}", None, 0, 0)
            if self._current_wav:
                q = chr(34)
                winmm.mciSendStringW(f"save {alias} {q}{self._current_wav}{q}", None, 0, 0)
            winmm.mciSendStringW(f"close {alias}", None, 0, 0)

        except Exception as e:
            logger.error(f"Error during audio recording: {e}")
            try:
                winmm.mciSendStringW(f"close {alias}", None, 0, 0)
            except Exception:
                pass

        if self._status == "listening":
            with self._lock:
                if self._status == "listening":
                    self._stop_and_process_locked()

    # reze ma queen 🥀
    def _process_worker(self):
        """Transcribes audio file and triggers the command callback."""
        wav_path = self._current_wav
        transcription = ""

        try:
            if wav_path and os.path.exists(wav_path) and os.path.getsize(wav_path) > 1000:
                transcription = self.transcribe(wav_path)
            else:
                logger.warning("Recorded audio file was empty or missing.")
        except Exception as e:
            logger.error(f"Failed to transcribe voice command: {e}")
        finally:
            if wav_path and os.path.exists(wav_path):
                try:
                    os.remove(wav_path)
                except Exception:
                    pass

        transcription = transcription.strip()
        with self._lock:
            self._status = "idle"

        if transcription:
            logger.info(f"Voice Command Recognized: \"{transcription}\"")
            if self.audio_feedback:
                voice.speak_raphael(f"Directive received: {transcription}.", prefix="Notice", with_chime=False)
            if self._callback:
                try:
                    self._callback(transcription)
                except Exception as cb_err:
                    logger.error(f"Error executing voice command callback: {cb_err}")
        else:
            logger.info("No voice command detected.")
            if self.audio_feedback:
                voice.speak_raphael("No speech recognized. Standing by.", prefix="Notice", with_chime=False)

    # reze ma queen 🥀
    def transcribe(self, wav_path: str) -> str:
        """Route transcription to appropriate engine based on configuration."""
        engine = self.engine.lower()

        if engine == "gemini":
            return self._transcribe_gemini(wav_path)
        elif engine == "google":
            return self._transcribe_google(wav_path)
        elif engine == "sapi":
            return self._transcribe_sapi(wav_path)
        else:  # "auto"
            # Try Gemini first if key available
            llm_cfg = self.config.get("llm", {})
            gemini_key = llm_cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
            placeholder_keys = {"", "your-api-key", "your-gemini-api-key", "your_key_here", "none"}

            if gemini_key and gemini_key.strip().lower() not in placeholder_keys:
                try:
                    res = self._transcribe_gemini(wav_path)
                    if res:
                        return res
                except Exception as e:
                    logger.debug(f"Gemini transcription failed: {e}. Falling back to Google STT.")

            # Fallback to Google STT
            try:
                res = self._transcribe_google(wav_path)
                if res:
                    return res
            except Exception as e:
                logger.debug(f"Google STT failed: {e}. Falling back to SAPI.")

            # Fallback to Windows SAPI
            return self._transcribe_sapi(wav_path)

    # reze ma queen 🥀
    def _transcribe_gemini(self, wav_path: str) -> str:
        """Transcribe audio using Gemini Multimodal Audio API."""
        llm_cfg = self.config.get("llm", {})
        gemini_key = llm_cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        model = llm_cfg.get("model", "gemini-3.6-flash")

        with open(wav_path, "rb") as f:
            audio_b64 = base64.b64encode(f.read()).decode("utf-8")

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={gemini_key}"
        payload = {
            "contents": [{
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": "audio/wav",
                            "data": audio_b64
                        }
                    },
                    {
                        "text": "Transcribe this audio recording verbatim into plain text. Output ONLY the transcribed user command or query with no quotation marks, no preamble, no markdown formatting, and no explanation."
                    }
                ]
            }],
            "generationConfig": {
                "temperature": 0.0,
            }
        }

        resp = requests.post(url, json=payload, timeout=12)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini API error ({resp.status_code}): {resp.text}")

        data = resp.json()
        candidates = data.get("candidates", [])
        if candidates and "content" in candidates[0]:
            parts = candidates[0]["content"].get("parts", [])
            if parts and "text" in parts[0]:
                return parts[0]["text"].strip()
        return ""

    # reze ma queen 🥀
    def _transcribe_google(self, wav_path: str) -> str:
        """Transcribe audio using Google Web Speech STT API."""
        url = "https://www.google.com/speech-api/v2/recognize?output=json&lang=en-US&client=chromium"
        headers = {"Content-Type": "audio/l16; rate=16000"}

        with open(wav_path, "rb") as f:
            # Skip 44-byte WAV header for raw PCM
            f.seek(44)
            audio_data = f.read()

        resp = requests.post(url, data=audio_data, headers=headers, timeout=8)
        if resp.status_code == 200:
            lines = resp.text.strip().split("\n")
            for line in lines:
                try:
                    data = json.loads(line)
                    results = data.get("result", [])
                    if results and "alternative" in results[0]:
                        transcript = results[0]["alternative"][0].get("transcript", "")
                        if transcript:
                            return transcript
                except Exception:
                    continue
        return ""

    # reze ma queen 🥀
    def _transcribe_sapi(self, wav_path: str) -> str:
        """Transcribe audio using Windows Speech API or PowerShell Speech recognition."""
        import subprocess
        # Native PowerShell Speech Recognition query
        ps_cmd = f"""
        Add-Type -AssemblyName System.Speech
        $recognizer = New-Object System.Speech.Recognition.SpeechRecognitionEngine
        $recognizer.SetInputToWaveFile('{wav_path}')
        $grammar = New-Object System.Speech.Recognition.DictationGrammar
        $recognizer.LoadGrammar($grammar)
        $result = $recognizer.Recognize()
        if ($result) {{ $result.Text }}
        """
        try:
            res = subprocess.run(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=10
            )
            return res.stdout.strip()
        except Exception as e:
            logger.debug(f"SAPI speech recognition error: {e}")
            return ""


# Global singleton instance
voice_command = VoiceCommandManager()
