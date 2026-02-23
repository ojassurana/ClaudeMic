"""Main loop: hotkey + state machine + orchestration."""

import enum
import logging
import queue
import signal
import threading
import time

from pynput import keyboard

from .constants import DEFAULT_TIMEOUT, DOUBLE_TAP_WINDOW, HOTKEY_COMBO
from .notifier import notify
from .recorder import AudioRecorder
from .transcriber import Transcriber
from .typer import type_text

logger = logging.getLogger(__name__)


class State(enum.Enum):
    IDLE = "idle"
    RECORDING = "recording"
    RECORDING_PERPETUAL = "recording_perpetual"


class Core:
    """Main orchestrator: hotkey detection, state machine, transcription loop."""

    def __init__(self):
        self._state = State.IDLE
        self._state_lock = threading.Lock()
        self._shutdown = threading.Event()

        # Double-tap detection
        self._last_press_time: float = 0.0

        # Timeout
        self._timeout_timer: threading.Timer | None = None

        # Transcription pipeline
        self._chunk_queue: queue.Queue[bytes] = queue.Queue()
        self._recorder = AudioRecorder(self._chunk_queue)
        self._transcriber: Transcriber | None = None
        self._worker_thread: threading.Thread | None = None

        # Track first transcription to avoid leading space
        self._first_chunk = True

    def run(self) -> None:
        """Start the main loop. Blocks until shutdown."""
        logger.info("ClaudeMic core starting")
        self._transcriber = Transcriber()

        # Register signal handlers for clean shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        # Parse hotkey combo
        hotkey = keyboard.HotKey(
            keyboard.HotKey.parse(HOTKEY_COMBO),
            self._on_hotkey,
        )

        def on_press(key):
            hotkey.press(self._listener.canonical(key))

        def on_release(key):
            hotkey.release(self._listener.canonical(key))

        self._listener = keyboard.Listener(on_press=on_press, on_release=on_release)
        self._listener.start()

        notify("ClaudeMic", "Ready — Cmd+Shift+M to toggle mic")
        logger.info("Hotkey listener started, waiting for input")

        # Block until shutdown
        self._shutdown.wait()

        # Cleanup
        self._stop_recording()
        self._listener.stop()
        logger.info("ClaudeMic core stopped")

    def _signal_handler(self, signum, frame) -> None:
        """Handle SIGTERM/SIGINT for clean shutdown."""
        logger.info("Received signal %s, shutting down", signum)
        self._shutdown.set()

    def _on_hotkey(self) -> None:
        """Called when Cmd+Shift+M is pressed."""
        now = time.monotonic()
        time_since_last = now - self._last_press_time
        self._last_press_time = now

        with self._state_lock:
            if self._state == State.IDLE:
                if time_since_last <= DOUBLE_TAP_WINDOW:
                    # Double-tap: perpetual mode
                    self._start_recording(perpetual=True)
                else:
                    # Single press: timed mode
                    self._start_recording(perpetual=False)
            else:
                # Any press while recording: stop
                self._stop_recording()

    def _start_recording(self, perpetual: bool) -> None:
        """Start recording and transcription. Must hold _state_lock."""
        if perpetual:
            self._state = State.RECORDING_PERPETUAL
            notify("ClaudeMic", "Perpetual mode ON (no timeout)")
            logger.info("Recording started (perpetual mode)")
        else:
            self._state = State.RECORDING
            notify("ClaudeMic", "Mic ON (5 min timeout)")
            logger.info("Recording started (5 min timeout)")
            # Start timeout timer
            self._timeout_timer = threading.Timer(DEFAULT_TIMEOUT, self._on_timeout)
            self._timeout_timer.daemon = True
            self._timeout_timer.start()

        self._first_chunk = True
        self._recorder.start()

        # Start transcription worker
        self._worker_thread = threading.Thread(
            target=self._transcription_worker, daemon=True
        )
        self._worker_thread.start()

    def _stop_recording(self) -> None:
        """Stop recording and transcription."""
        if self._state == State.IDLE:
            return

        self._state = State.IDLE

        # Cancel timeout
        if self._timeout_timer is not None:
            self._timeout_timer.cancel()
            self._timeout_timer = None

        # Stop recorder (flushes remaining audio)
        self._recorder.stop()

        # Signal worker to exit
        self._chunk_queue.put(None)
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=10)
            self._worker_thread = None

        # Drain any leftover items from queue
        while not self._chunk_queue.empty():
            try:
                self._chunk_queue.get_nowait()
            except queue.Empty:
                break

        notify("ClaudeMic", "Mic OFF")
        logger.info("Recording stopped")

    def _on_timeout(self) -> None:
        """Called when timed recording mode reaches its timeout."""
        with self._state_lock:
            if self._state == State.RECORDING:
                logger.info("Recording timed out")
                self._stop_recording()

    def _transcription_worker(self) -> None:
        """Worker thread that processes audio chunks from the queue."""
        logger.debug("Transcription worker started")
        while True:
            try:
                chunk = self._chunk_queue.get(timeout=1.0)
            except queue.Empty:
                # Check if we should still be running
                if self._state == State.IDLE:
                    break
                continue

            if chunk is None:
                break

            text = self._transcriber.transcribe(chunk)
            if text:
                # Skip leading space for the very first chunk
                if self._first_chunk:
                    self._first_chunk = False
                    text = text.lstrip()
                type_text(text)

        logger.debug("Transcription worker stopped")
