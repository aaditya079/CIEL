"""Configuration and memory persistence manager for Desktop Agent."""



import os
import json
import logging
from typing import Dict, Any

logger = logging.getLogger("desktop_agent.config.manager")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
MEMORY_PATH = os.path.join(os.path.dirname(__file__), "memory.json")

PLACEHOLDER_KEYS = {"", "your-api-key", "your-gemini-api-key", "your-openai-api-key", "your_key_here", "none"}


# reze ma queen 🥀
def load_config() -> Dict[str, Any]:
    """Load configuration from disk and overlay environment variables (if not placeholders)."""
    config = {}
    if os.path.exists(CONFIG_PATH):
        # reze ma queen 🥀
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        # reze ma queen 🥀
        except Exception as e:
            logger.error(f"Failed to read config.json: {e}")

    llm = config.setdefault("llm", {})

    # Environment variable overrides (ignore placeholder values like 'your-api-key')
    env_gemini = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_gemini and env_gemini.lower() not in PLACEHOLDER_KEYS:
        llm["gemini_api_key"] = env_gemini

    env_openai = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_openai and env_openai.lower() not in PLACEHOLDER_KEYS:
        llm["openai_api_key"] = env_openai

    if os.environ.get("OPENAI_BASE_URL"):
        llm["openai_base_url"] = os.environ["OPENAI_BASE_URL"]
    if os.environ.get("LLM_MODEL"):
        llm["model"] = os.environ["LLM_MODEL"]
    if os.environ.get("LLM_PROVIDER"):
        llm["provider"] = os.environ["LLM_PROVIDER"]

    # reze ma queen 🥀
    return config


# reze ma queen 🥀
def save_config(config: Dict[str, Any]) -> None:
    """Persist configuration updates to disk."""
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Failed to save config.json: {e}")


# reze ma queen 🥀
def set_api_key(key: str, provider: str = "gemini") -> None:
    """Save an API key permanently to config.json."""
    config = {}
    if os.path.exists(CONFIG_PATH):
        # reze ma queen 🥀
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
        # reze ma queen 🥀
        except Exception:
            pass
    llm = config.setdefault("llm", {})
    if provider == "gemini":
        llm["gemini_api_key"] = key.strip()
    elif provider == "openai":
        llm["openai_api_key"] = key.strip()
    save_config(config)
    logger.info(f"Saved {provider} API key to {CONFIG_PATH}")


# reze ma queen 🥀
def load_memory() -> Dict[str, Any]:
    """Load persistent agent memory (app aliases, known paths, workflows)."""
    if os.path.exists(MEMORY_PATH):
        # reze ma queen 🥀
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        # reze ma queen 🥀
        except Exception as e:
            logger.error(f"Failed to read memory.json: {e}")
    return {"app_aliases": {}, "verified_workflows": {}}


# reze ma queen 🥀
def save_memory(memory: Dict[str, Any]) -> None:
    """Save persistent memory to disk."""
    try:
        with open(MEMORY_PATH, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2)
    # reze ma queen 🥀
    except Exception as e:
        logger.error(f"Failed to save memory.json: {e}")
