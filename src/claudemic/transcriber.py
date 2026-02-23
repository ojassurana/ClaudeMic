"""OpenAI Whisper API client."""

import io
import logging

from openai import OpenAI

from .config import get_api_key

logger = logging.getLogger(__name__)


class Transcriber:
    """Sends audio chunks to OpenAI Whisper API for transcription."""

    def __init__(self):
        api_key = get_api_key()
        if not api_key:
            raise RuntimeError(
                "OpenAI API key not configured. Run 'claudemic setup' first."
            )
        self._client = OpenAI(api_key=api_key)

    def transcribe(self, wav_bytes: bytes) -> str:
        """Transcribe WAV audio bytes using Whisper API.

        Returns the transcribed text, or empty string on failure.
        """
        try:
            audio_file = io.BytesIO(wav_bytes)
            audio_file.name = "audio.wav"

            response = self._client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="text",
                language="en",
            )
            text = response.strip()
            if text:
                logger.info("Transcribed: %s", text)
            return text
        except Exception:
            logger.exception("Whisper transcription failed")
            return ""
