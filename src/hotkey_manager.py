"""
Hotkey Manager - Global hotkey registration and monitoring

This module provides global hotkey registration using pynput, with thread-safe
communication to the Qt main thread via signals.

Classes:
    HotkeyManager: Global hotkey listener and manager
"""

from pynput import keyboard
from PySide6.QtCore import QObject, Signal
import logging

logger = logging.getLogger(__name__)


class HotkeyManager(QObject):
    """Global hotkey registration and monitoring."""

    hotkey_pressed = Signal()  # Thread-safe signal for hotkey press

    def __init__(self, hotkey_string="ctrl+shift+space"):
        """
        Initialize hotkey manager.

        Args:
            hotkey_string: Hotkey combination (e.g., "ctrl+shift+space")
        """
        super().__init__()
        self.hotkey_string = hotkey_string
        self.hotkey_combination = self._parse_hotkey(hotkey_string)
        self.current_keys = set()
        self.listener = None

    def _parse_hotkey(self, hotkey_string):
        """
        Parse hotkey string into pynput key set.

        Args:
            hotkey_string: String like "ctrl+shift+space"

        Returns:
            Set of pynput Key objects
        """
        keys = set()
        parts = hotkey_string.lower().split("+")

        for part in parts:
            part = part.strip()
            if part == "ctrl":
                keys.add(keyboard.Key.ctrl_l)
            elif part == "shift":
                keys.add(keyboard.Key.shift)
            elif part == "alt":
                keys.add(keyboard.Key.alt_l)
            elif part == "space":
                keys.add(keyboard.Key.space)
            else:
                # Single character key
                try:
                    keys.add(keyboard.KeyCode.from_char(part))
                except:
                    logger.warning(f"Could not parse key: {part}")

        return keys

    def start(self):
        """Start listening for hotkey presses."""
        if self.listener is not None:
            logger.warning("Hotkey listener already running")
            return

        self.listener = keyboard.Listener(
            on_press=self._on_press, on_release=self._on_release
        )
        self.listener.start()

    def stop(self):
        """Stop listening for hotkey presses."""
        if self.listener is not None:
            self.listener.stop()
            self.listener = None

    def _on_press(self, key):
        """Handle key press event (runs in pynput thread)."""
        self.current_keys.add(key)

        # Check if hotkey combination is pressed
        if self._is_hotkey_pressed():
            self.hotkey_pressed.emit()  # Thread-safe signal

    def _on_release(self, key):
        """Handle key release event (runs in pynput thread)."""
        try:
            self.current_keys.discard(key)
        except KeyError:
            pass

    def _is_hotkey_pressed(self):
        """Check if current key combination matches registered hotkey."""
        # For ctrl+shift+space, check if ctrl (left or right) is pressed
        has_ctrl = (
            keyboard.Key.ctrl_l in self.current_keys
            or keyboard.Key.ctrl_r in self.current_keys
        )
        has_shift = (
            keyboard.Key.shift in self.current_keys
            or keyboard.Key.shift_r in self.current_keys
        )
        has_space = keyboard.Key.space in self.current_keys

        # Check if all required keys are pressed
        if (
            "ctrl" in self.hotkey_string.lower()
            and "shift" in self.hotkey_string.lower()
            and "space" in self.hotkey_string.lower()
        ):
            return has_ctrl and has_shift and has_space

        # Generic check for any hotkey combination
        # For now, support common patterns
        return has_ctrl and has_shift and has_space
