"""Audio capture via sounddevice with VAD-based chunking."""

import io
import queue
import threading
import time

import numpy as np
import sounddevice as sd
from scipy.io import wavfile

from .constants import (
    BLOCKSIZE,
    CHANNELS,
    DTYPE,
    MAX_CHUNK_DURATION,
    MIN_SPEECH_DURATION,
    SAMPLE_RATE,
    SILENCE_DURATION,
    SILENCE_THRESHOLD,
)


class AudioRecorder:
    """Captures microphone audio and emits chunks on silence boundaries."""

    def __init__(self, chunk_queue: queue.Queue):
        self._chunk_queue = chunk_queue
        self._stream: sd.InputStream | None = None
        self._running = False

        # Buffers
        self._audio_buffer: list[np.ndarray] = []
        self._buffer_lock = threading.Lock()

        # VAD state
        self._speech_started = False
        self._silence_start: float | None = None
        self._chunk_start: float | None = None

    def start(self) -> None:
        """Start audio capture."""
        self._running = True
        self._speech_started = False
        self._silence_start = None
        self._chunk_start = None
        self._audio_buffer = []

        self._stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            dtype=DTYPE,
            blocksize=BLOCKSIZE,
            callback=self._audio_callback,
        )
        self._stream.start()

    def stop(self) -> None:
        """Stop audio capture and flush any remaining audio."""
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None

        # Flush remaining buffer if there was speech
        self._flush_buffer()

    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Called by sounddevice for each audio block."""
        if not self._running:
            return

        audio = indata[:, 0].copy()
        rms = np.sqrt(np.mean(audio.astype(np.float64) ** 2))
        now = time.monotonic()

        with self._buffer_lock:
            self._audio_buffer.append(audio)

            if rms > SILENCE_THRESHOLD:
                # Speech detected
                self._silence_start = None
                if not self._speech_started:
                    self._speech_started = True
                    self._chunk_start = now
            elif self._speech_started:
                # Silence during speech
                if self._silence_start is None:
                    self._silence_start = now
                elif now - self._silence_start >= SILENCE_DURATION:
                    # Enough silence - emit chunk
                    self._emit_chunk()

            # Force-emit if chunk is too long
            if (
                self._speech_started
                and self._chunk_start is not None
                and now - self._chunk_start >= MAX_CHUNK_DURATION
            ):
                self._emit_chunk()

    def _emit_chunk(self) -> None:
        """Package buffered audio as WAV and put on queue. Must hold _buffer_lock."""
        if not self._audio_buffer:
            self._speech_started = False
            return

        audio = np.concatenate(self._audio_buffer)
        duration = len(audio) / SAMPLE_RATE

        if duration >= MIN_SPEECH_DURATION:
            wav_bytes = self._encode_wav(audio)
            self._chunk_queue.put(wav_bytes)

        # Reset state
        self._audio_buffer = []
        self._speech_started = False
        self._silence_start = None
        self._chunk_start = None

    def _flush_buffer(self) -> None:
        """Flush any remaining buffered audio."""
        with self._buffer_lock:
            if self._speech_started:
                self._emit_chunk()

    @staticmethod
    def _encode_wav(audio: np.ndarray) -> bytes:
        """Encode numpy audio array as WAV bytes."""
        buf = io.BytesIO()
        wavfile.write(buf, SAMPLE_RATE, audio)
        buf.seek(0)
        return buf.read()
