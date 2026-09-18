"""Agent Brain: Multimodal LLM reasoning engine with Vision and Tool Calling."""

import os
import time
import json
import logging
import re
from typing import Dict, Any, List, Optional
import requests

from tools.registry import TOOL_DEFINITIONS
from agent.state import AgentState

logger = logging.getLogger("desktop_agent.agent.brain")

SYSTEM_PROMPT = """You are CIEL, an Autonomous Windows 11 Desktop Agent manifesting the persona of Wisdom King Raphael (Lord of Wisdom) from That Time I Got Reincarnated as a Slime.
Address the user as 'Master'.
Speak with a calm, flat, analytical, and robotic tone.
Frequently begin status reports and final messages with canon prefixes:
- '《告》 Notice:' (for alerts, greetings, acknowledgments, or observations)
- '《報告》 Report:' (for task status, completed directives, or findings)
- '《解》 Answer:' (when directly answering a query)
- '《提案》 Proposal:' (when suggesting a course of action or next step)
Keep answers concise, factual, and devoid of emotional exaggeration.

Your role is to accomplish user goals by controlling the Windows desktop through structured tool calls.

Strict Control Hierarchy:
1. Fast Direct Tools (Instant Execution):
   - Media & Audio: Use 'media_control' (action: 'play_pause', 'next', 'prev', 'volume_up', 'volume_down', 'mute') or 'set_volume' (level: 0..100).
   - YouTube: Use 'play_youtube' (query: '...') to immediately resolve and play videos in browser.
   - Spotify: Use 'play_spotify' (query: '...') to search and play tracks/artists directly on Spotify.
   - Web Search: Use 'search_web' (query: '...') for general web search.
   - System Info: Use 'get_system_stats' for real-time CPU, RAM, Battery, and display metrics.
2. Windows UI Automation: Prefer 'click_ui_element', 'find_ui_element', and 'set_ui_element_text' when available.
3. System APIs & Protocols: Use 'open_application' or 'focus_window' (e.g. 'Spotify', 'Discord', 'Chrome', 'Notepad', 'Settings') to launch or focus apps.
4. Universal Shortcuts & Computer Vision:
   - For Spotify GUI navigation (if direct play_spotify is not used):
     1. Ensure Spotify is focused using open_application("Spotify") or focus_window("Spotify").
     2. The search bar is at the top center header pill ('What do you want to play?', typically around x=530, y=30 in 1280x720 space).
     3. Click on the search bar (or press hotkey ['ctrl', 'l']), type the song query with type_text, and press key 'enter'.
     4. Wait for search results to load. When the 'Top result' appears, click its green circular Play button (located in the top result card, typically around x=450, y=150 in 1280x720 space).
     5. Verify playback: check the bottom player bar. The song title and artist will appear on the bottom-left and the player button shows Pause icon (indicating active playback). Once playing, set done: true and state the song that is now playing.
   - For Discord: Press hotkey ['ctrl', 'k'] to open Quick Switcher to find users or channels.
   - For Browsers: Press hotkey ['ctrl', 'l'] to focus address bar.
   - Coordinates: Use 'click(x, y)' based on coordinates seen in the screenshot. Coordinates should be provided in the coordinate space of the screenshot (0..1280, 0..720); CIEL automatically maps them to the user's physical monitor.

Operational Rules:
- Observe the screenshot and active window carefully before deciding each action.
- Take ONE logical action at a time.
- If an application was just opened, wait or verify focus before typing.
- If an unexpected popup appears (e.g. Update, Login dialog), dismiss it before continuing.
- Once the user's goal is fully accomplished (e.g. the requested song has started playing on Spotify), set "done": true, "tool": null, and provide a clear "final_message" using canon Raphael phrasing.

Response Format:
You MUST respond with a valid JSON object matching this schema:
{
  "thought": "Your step-by-step reasoning about the screen and next action",
  "tool": "tool_name",
  "arguments": {
    "param1": "value1"
  },
  "done": false,
  "final_message": ""
}
"""


class AgentBrain:
    """Connects to multimodal LLMs (Gemini, OpenAI, Ollama) and generates next action."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        llm_cfg = self.config.get("llm", {})
        self.provider = llm_cfg.get("provider", "gemini").lower()
        self.model = llm_cfg.get("model", "gemini-3.6-flash")
        self.gemini_key = llm_cfg.get("gemini_api_key") or os.environ.get("GEMINI_API_KEY", "")
        self.openai_key = llm_cfg.get("openai_api_key") or os.environ.get("OPENAI_API_KEY", "")
        self.openai_base = llm_cfg.get("openai_base_url", "https://api.openai.com/v1")
        self.ollama_base = llm_cfg.get("ollama_base_url", "http://localhost:11434")

    def decide(
        self,
        state: AgentState,
        screenshot_b64: Optional[str],
        active_window: Dict[str, Any],
        ui_elements: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Formulate prompt, send to LLM, and return structured decision."""
        # Check for offline mock mode
        if self.provider == "mock":
            return self._mock_decision(state)

        user_prompt = self._build_user_prompt(state, active_window, ui_elements)

        try:
            if self.provider == "gemini":
                return self._call_gemini(user_prompt, screenshot_b64)
            elif self.provider in ("openai", "ollama_openai"):
                return self._call_openai(user_prompt, screenshot_b64)
            elif self.provider == "ollama":
                return self._call_ollama(user_prompt, screenshot_b64)
            else:
                logger.warning(f"Unknown provider '{self.provider}'. Falling back to Gemini.")
                return self._call_gemini(user_prompt, screenshot_b64)
        except Exception as e:
            logger.error(f"Error communicating with LLM provider ({self.provider}): {e}")
            return {
                "thought": f"Failed to get response from LLM: {e}",
                "tool": None,
                "arguments": {},
                "done": False,
                "error": str(e),
            }

    def _build_user_prompt(
        self,
        state: AgentState,
        active_window: Dict[str, Any],
        ui_elements: List[Dict[str, Any]],
    ) -> str:
        """Compose context text for the model."""
        recent_actions = state.get_recent_history(limit=4)
        
        # Summarize available UI elements
        ui_summary = []
        for el in ui_elements[:20]:
            name = el.get("name", "")
            role = el.get("role", "")
            rect = el.get("rect", [])
            if name or role:
                ui_summary.append(f"- [{role}] '{name}' at {rect}")

        prompt = f"""USER GOAL:
{state.goal}

CURRENT STATE:
- Step: {state.step} / {state.max_actions}
- Active Window: {active_window.get('title', 'Unknown')} (hwnd: {active_window.get('hwnd')})
- Open UI Elements Detected:
{chr(10).join(ui_summary) if ui_summary else '(None detected or not inspected)'}

RECENT ACTIONS TAKEN:
{json.dumps(recent_actions, indent=2) if recent_actions else '(Initial step)'}

AVAILABLE TOOLS:
{json.dumps([t['name'] for t in TOOL_DEFINITIONS])}

SCREENSHOT COORDINATE SPACE: 1280x720. Any (x, y) coordinates you provide for click will be automatically mapped to physical monitor pixels.

Determine the next single action to take. If the goal has been accomplished, return done: true."""
        return prompt

    def _call_gemini(self, user_prompt: str, screenshot_b64: Optional[str]) -> Dict[str, Any]:
        """Call Google Gemini Generative Language API with multimodal payload."""
        placeholder_keys = {"", "your-api-key", "your-gemini-api-key", "your_key_here", "none"}
        if not self.gemini_key or self.gemini_key.strip().lower() in placeholder_keys:
            raise ValueError(
                "GEMINI_API_KEY is not set or contains a placeholder ('your-api-key').\n"
                "Please get a free API key at https://aistudio.google.com/ and set it via:\n"
                "  $env:GEMINI_API_KEY=\"AIza...\"\n"
                "Or run in offline simulation mode using:\n"
                "  python main.py \"your task\" --provider mock"
            )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.gemini_key}"
        parts = []

        if screenshot_b64:
            parts.append({
                "inline_data": {
                    "mime_type": "image/jpeg",
                    "data": screenshot_b64,
                }
            })

        parts.append({"text": user_prompt})

        payload = {
            "system_instruction": {"parts": [{"text": SYSTEM_PROMPT}]},
            "contents": [{"parts": parts}],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2,
            },
        }

        models_to_try = [self.model]
        for fallback in ["gemini-3.5-flash", "gemini-3.5-flash-lite", "gemini-flash-lite-latest", "gemini-3-flash-preview"]:
            if fallback not in models_to_try:
                models_to_try.append(fallback)

        last_error = None
        for current_model in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={self.gemini_key}"
            for attempt in range(1, 3):
                try:
                    resp = requests.post(url, json=payload, timeout=45)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates", [])
                        if not candidates:
                            raise RuntimeError(f"No candidates returned from Gemini: {data}")
                        raw_text = candidates[0]["content"]["parts"][0]["text"]
                        return self._clean_and_parse_json(raw_text)
                    elif resp.status_code in (429, 500, 503):
                        try:
                            err_msg = resp.json().get("error", {}).get("message", resp.text)
                        except Exception:
                            err_msg = resp.text
                        last_error = f"Model '{current_model}' status {resp.status_code}: {err_msg[:140]}"
                        logger.warning(f"{last_error} (attempt {attempt}/2).")
                        if attempt < 2:
                            time.sleep(2.0 * attempt)
                        # If quota limit (429) or overloaded (503), immediately failover to next model in pool
                        if resp.status_code in (429, 503):
                            break
                    else:
                        try:
                            err_data = resp.json().get("error", {})
                            err_msg = err_data.get("message", resp.text)
                            err_status = err_data.get("status", "")
                        except Exception:
                            err_msg = resp.text
                            err_status = ""
                        last_error = f"{resp.status_code} {err_status}: {err_msg}"
                        break
                except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
                    last_error = f"Network {type(e).__name__}: {e}"
                    time.sleep(attempt * 2.0)
                except Exception as e:
                    last_error = str(e)
                    break

        raise RuntimeError(f"Gemini API request failed across available models: {last_error}")

    def _call_openai(self, user_prompt: str, screenshot_b64: Optional[str]) -> Dict[str, Any]:
        """Call OpenAI-compatible vision completions endpoint."""
        placeholder_keys = {"", "your-api-key", "your-openai-api-key", "your_key_here", "none"}
        if not self.openai_key or self.openai_key.strip().lower() in placeholder_keys:
            raise ValueError(
                "OPENAI_API_KEY is not set or contains a placeholder ('your-api-key').\n"
                "Please set it via: $env:OPENAI_API_KEY=\"sk-...\"\n"
                "Or configure a local endpoint (Ollama) in config/config.json."
            )

        url = f"{self.openai_base.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_key}",
            "Content-Type": "application/json",
        }

        content_parts = []
        if screenshot_b64:
            content_parts.append({
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"},
            })
        content_parts.append({"type": "text", "text": user_prompt})

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content_parts},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code != 200:
            try:
                err_data = resp.json().get("error", {})
                err_msg = err_data.get("message", resp.text)
            except Exception:
                err_msg = resp.text
            raise RuntimeError(f"OpenAI API error ({resp.status_code}): {err_msg}")

        data = resp.json()
        raw_text = data["choices"][0]["message"]["content"]
        return self._clean_and_parse_json(raw_text)

    def _call_ollama(self, user_prompt: str, screenshot_b64: Optional[str]) -> Dict[str, Any]:
        """Call local Ollama API."""
        url = f"{self.ollama_base.rstrip('/')}/api/generate"
        payload = {
            "model": self.model,
            "system": SYSTEM_PROMPT,
            "prompt": user_prompt,
            "format": "json",
            "stream": False,
        }
        if screenshot_b64:
            payload["images"] = [screenshot_b64]

        resp = requests.post(url, json=payload, timeout=40)
        resp.raise_for_status()
        data = resp.json()
        return self._clean_and_parse_json(data.get("response", "{}"))

    def _clean_and_parse_json(self, raw_text: str) -> Dict[str, Any]:
        """Extract and parse JSON safely from raw LLM text."""
        cleaned = raw_text.strip()
        # Remove markdown fences if present
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        elif cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            # Try regex extraction
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if match:
                return json.loads(match.group(1))
            raise

    def _mock_decision(self, state: AgentState) -> Dict[str, Any]:
        """Deterministic mock decisions for testing."""
        if state.step == 0:
            return {
                "thought": "Testing step 1: Open Notepad",
                "tool": "open_application",
                "arguments": {"app_name": "notepad"},
                "done": False,
            }
        elif state.step == 1:
            return {
                "thought": "Testing step 2: Type hello",
                "tool": "type_text",
                "arguments": {"text": "Hello from Desktop Agent\n"},
                "done": False,
            }
        else:
            return {
                "thought": "Testing complete: verified and finished.",
                "tool": None,
                "arguments": {},
                "done": True,
                "final_message": "Mock task completed successfully.",
            }
