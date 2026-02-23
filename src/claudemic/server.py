"""MCP server exposing voice-to-text tools for Claude Code."""

from mcp.server.fastmcp import FastMCP

from .config import get_api_key, set_api_key
from .recorder import record_utterance
from .transcriber import Transcriber

mcp = FastMCP("claudemic")


@mcp.tool()
def listen(timeout: float = 60.0) -> str:
    """Record audio from the microphone and transcribe it to text.

    Listens for a single utterance (stops after detecting silence following speech).
    Returns the transcribed text.

    Args:
        timeout: Maximum seconds to wait for speech (default 60).
    """
    api_key = get_api_key()
    if not api_key:
        return "Error: OpenAI API key not configured. Use the 'setup' tool or set OPENAI_API_KEY."

    wav_bytes = record_utterance(timeout=timeout)
    if wav_bytes is None:
        return "No speech detected within timeout."

    transcriber = Transcriber()
    text = transcriber.transcribe(wav_bytes)
    if not text:
        return "Transcription returned empty result."

    return text


@mcp.tool()
def setup(api_key: str) -> str:
    """Configure the OpenAI API key for Whisper transcription.

    Args:
        api_key: Your OpenAI API key (starts with 'sk-').
    """
    api_key = api_key.strip()
    if not api_key:
        return "Error: API key cannot be empty."

    set_api_key(api_key)
    return "API key saved to ~/.claudemic/config.json"


@mcp.tool()
def status() -> str:
    """Check if ClaudeMic is properly configured.

    Reports whether the API key is set and an audio input device is available.
    """
    lines = []

    # Check API key
    key = get_api_key()
    if key:
        masked = key[:8] + "..." + key[-4:]
        lines.append(f"API key: configured ({masked})")
    else:
        lines.append("API key: NOT configured")

    # Check audio device
    try:
        import sounddevice as sd

        device = sd.query_devices(kind="input")
        lines.append(f"Audio input: {device['name']}")
    except Exception as e:
        lines.append(f"Audio input: unavailable ({e})")

    return "\n".join(lines)


if __name__ == "__main__":
    mcp.run(transport="stdio")
