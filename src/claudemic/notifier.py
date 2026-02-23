"""macOS notifications for status feedback."""

import logging
import subprocess

logger = logging.getLogger(__name__)

_BUNDLE_ID = "com.anthropic.claudemic"


def notify(title: str, message: str) -> None:
    """Send a macOS notification using osascript."""
    try:
        script = (
            f'display notification "{_escape(message)}" '
            f'with title "{_escape(title)}"'
        )
        subprocess.Popen(
            ["osascript", "-e", script],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        logger.debug("Notification failed", exc_info=True)


def _escape(text: str) -> str:
    """Escape double quotes for AppleScript."""
    return text.replace("\\", "\\\\").replace('"', '\\"')
