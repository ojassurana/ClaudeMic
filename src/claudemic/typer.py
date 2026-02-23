"""Keyboard simulation via pynput."""

import logging
import time

from pynput.keyboard import Controller, Key

logger = logging.getLogger(__name__)

_keyboard = Controller()

# Small delay between keystrokes to avoid dropped characters
_KEYSTROKE_DELAY = 0.008


def type_text(text: str) -> None:
    """Simulate typing the given text string.

    Adds a leading space if text doesn't start with punctuation,
    to separate from previously typed words.
    """
    if not text:
        return

    # Add leading space to separate from previous transcription
    if text[0].isalnum():
        text = " " + text

    logger.debug("Typing: %r", text)
    for char in text:
        _keyboard.type(char)
        time.sleep(_KEYSTROKE_DELAY)
