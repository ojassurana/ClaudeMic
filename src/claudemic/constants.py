"""Defaults, paths, and audio settings."""

import os
from pathlib import Path

# Paths
CONFIG_DIR = Path(os.environ.get("CLAUDEMIC_CONFIG_DIR", Path.home() / ".claudemic"))
CONFIG_FILE = CONFIG_DIR / "config.json"
PID_FILE = CONFIG_DIR / "claudemic.pid"
LOG_FILE = CONFIG_DIR / "claudemic.log"

# Audio settings
SAMPLE_RATE = 16000  # 16kHz mono - optimal for Whisper
CHANNELS = 1
DTYPE = "int16"
BLOCKSIZE = 1024  # frames per sounddevice callback

# VAD (voice activity detection)
SILENCE_THRESHOLD = 500  # RMS amplitude below which we consider silence
SILENCE_DURATION = 0.8  # seconds of silence to trigger chunk boundary
MIN_SPEECH_DURATION = 0.3  # minimum seconds of speech to form a chunk
MAX_CHUNK_DURATION = 30.0  # max seconds per chunk (Whisper limit is 30s)

# Hotkey
HOTKEY_COMBO = "<cmd>+<shift>+m"
DOUBLE_TAP_WINDOW = 0.4  # seconds between presses to count as double-tap

# Timeouts
DEFAULT_TIMEOUT = 300  # 5 minutes for single-press mode
