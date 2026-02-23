"""Config load/save (~/.claudemic/config.json)."""

import json
import os
from pathlib import Path

from .constants import CONFIG_DIR, CONFIG_FILE


def ensure_config_dir() -> Path:
    """Create config directory if it doesn't exist."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    return CONFIG_DIR


def load_config() -> dict:
    """Load config from disk. Returns empty dict if no config exists."""
    if not CONFIG_FILE.exists():
        return {}
    return json.loads(CONFIG_FILE.read_text())


def save_config(config: dict) -> None:
    """Save config to disk with restricted permissions."""
    ensure_config_dir()
    CONFIG_FILE.write_text(json.dumps(config, indent=2) + "\n")
    os.chmod(CONFIG_FILE, 0o600)


def get_api_key() -> str | None:
    """Get OpenAI API key from config or environment."""
    env_key = os.environ.get("OPENAI_API_KEY")
    if env_key:
        return env_key
    config = load_config()
    return config.get("openai_api_key")


def set_api_key(key: str) -> None:
    """Store OpenAI API key in config."""
    config = load_config()
    config["openai_api_key"] = key
    save_config(config)
