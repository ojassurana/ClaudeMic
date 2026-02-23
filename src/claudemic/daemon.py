"""Background process management and PID file handling."""

import logging
import os
import signal
import subprocess
import sys

from .constants import CONFIG_DIR, LOG_FILE, PID_FILE

logger = logging.getLogger(__name__)


def is_running() -> bool:
    """Check if the daemon is currently running."""
    pid = _read_pid()
    if pid is None:
        return False
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        # Stale PID file
        _remove_pid()
        return False


def start_daemon() -> bool:
    """Start the daemon as a detached background process.

    Returns True if started successfully, False if already running.
    """
    if is_running():
        return False

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    log_fd = open(LOG_FILE, "a")

    proc = subprocess.Popen(
        [sys.executable, "-m", "claudemic.cli", "_run"],
        stdout=log_fd,
        stderr=log_fd,
        start_new_session=True,
    )

    log_fd.close()

    _write_pid(proc.pid)
    logger.info("Daemon started with PID %d", proc.pid)
    return True


def stop_daemon() -> bool:
    """Stop the running daemon.

    Returns True if stopped successfully, False if not running.
    """
    pid = _read_pid()
    if pid is None:
        return False

    try:
        os.kill(pid, signal.SIGTERM)
    except OSError:
        pass

    _remove_pid()
    logger.info("Daemon stopped (PID %d)", pid)
    return True


def _read_pid() -> int | None:
    """Read PID from file."""
    if not PID_FILE.exists():
        return None
    try:
        return int(PID_FILE.read_text().strip())
    except (ValueError, OSError):
        return None


def _write_pid(pid: int) -> None:
    """Write PID to file."""
    PID_FILE.write_text(str(pid) + "\n")


def _remove_pid() -> None:
    """Remove PID file."""
    try:
        PID_FILE.unlink()
    except FileNotFoundError:
        pass
