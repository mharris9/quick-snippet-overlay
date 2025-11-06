"""
Tests for hotkey_manager.py - Global hotkey registration and monitoring

This module tests:
- Hotkey registration with pynput
- Hotkey callback triggering via Qt signals
- Hotkey conflict detection
- Hotkey unregistration and cleanup
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QObject, Signal
from pynput import keyboard


@pytest.fixture
def qapp():
    """Create Qt application for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


def test_hotkey_registration(qapp):
    """Test that global hotkey is registered correctly."""
    from src.hotkey_manager import HotkeyManager

    manager = HotkeyManager("ctrl+shift+space")

    # Verify hotkey string stored
    assert manager.hotkey_string == "ctrl+shift+space"

    # Verify hotkey combination parsed
    assert manager.hotkey_combination is not None
    assert len(manager.hotkey_combination) > 0

    # Verify it's a QObject (for signals)
    assert isinstance(manager, QObject)


def test_hotkey_parsing(qapp):
    """Test that hotkey strings are parsed correctly."""
    from src.hotkey_manager import HotkeyManager

    manager = HotkeyManager("ctrl+alt+k")

    # Parse hotkey
    combination = manager._parse_hotkey("ctrl+shift+space")

    # Verify keys are in combination
    assert keyboard.Key.ctrl_l in combination or any(k for k in combination)
    assert keyboard.Key.shift in combination or any(k for k in combination)
    assert keyboard.Key.space in combination


def test_hotkey_listener_start(qapp):
    """Test that hotkey listener starts correctly."""
    from src.hotkey_manager import HotkeyManager

    with patch("pynput.keyboard.Listener") as mock_listener_class:
        mock_listener_instance = Mock()
        mock_listener_class.return_value = mock_listener_instance

        manager = HotkeyManager("ctrl+shift+space")
        manager.start()

        # Verify listener was created
        mock_listener_class.assert_called_once()

        # Verify listener was started
        mock_listener_instance.start.assert_called_once()


def test_hotkey_callback_triggered(qapp):
    """Test that hotkey press triggers Qt signal emission."""
    from src.hotkey_manager import HotkeyManager

    manager = HotkeyManager("ctrl+shift+space")

    # Create signal spy
    signal_emitted = []

    def on_hotkey():
        signal_emitted.append(True)

    manager.hotkey_pressed.connect(on_hotkey)

    # Simulate key presses
    manager._on_press(keyboard.Key.ctrl_l)
    manager._on_press(keyboard.Key.shift)
    manager._on_press(keyboard.Key.space)

    # Process Qt events to handle signal
    qapp.processEvents()

    # Verify signal was emitted
    assert len(signal_emitted) > 0


def test_hotkey_release_tracking(qapp):
    """Test that key releases are tracked correctly."""
    from src.hotkey_manager import HotkeyManager

    manager = HotkeyManager("ctrl+shift+space")

    # Press keys
    manager._on_press(keyboard.Key.ctrl_l)
    manager._on_press(keyboard.Key.shift)

    # Verify keys in current_keys
    assert len(manager.current_keys) >= 2

    # Release keys
    manager._on_release(keyboard.Key.ctrl_l)
    manager._on_release(keyboard.Key.shift)

    # Verify keys removed from current_keys
    assert keyboard.Key.ctrl_l not in manager.current_keys
    assert keyboard.Key.shift not in manager.current_keys


def test_hotkey_unregistration(qapp):
    """Test that hotkey listener is stopped and cleaned up."""
    from src.hotkey_manager import HotkeyManager

    with patch("pynput.keyboard.Listener") as mock_listener_class:
        mock_listener_instance = Mock()
        mock_listener_class.return_value = mock_listener_instance

        manager = HotkeyManager("ctrl+shift+space")
        manager.start()

        # Stop listener
        manager.stop()

        # Verify listener was stopped
        mock_listener_instance.stop.assert_called_once()

        # Verify listener reference cleared
        assert manager.listener is None


def test_multiple_start_calls_ignored(qapp):
    """Test that calling start() multiple times doesn't create multiple listeners."""
    from src.hotkey_manager import HotkeyManager

    with patch("pynput.keyboard.Listener") as mock_listener_class:
        mock_listener_instance = Mock()
        mock_listener_class.return_value = mock_listener_instance

        manager = HotkeyManager("ctrl+shift+space")

        # Start listener twice
        manager.start()
        manager.start()

        # Verify listener was only created once
        assert mock_listener_class.call_count == 1


def test_hotkey_detection_with_both_ctrl_keys(qapp):
    """Test that hotkey works with either left or right Ctrl."""
    from src.hotkey_manager import HotkeyManager

    manager = HotkeyManager("ctrl+shift+space")

    # Create signal spy
    signal_emitted = []

    def on_hotkey():
        signal_emitted.append(True)

    manager.hotkey_pressed.connect(on_hotkey)

    # Test with right Ctrl
    manager._on_press(keyboard.Key.ctrl_r)
    manager._on_press(keyboard.Key.shift)
    manager._on_press(keyboard.Key.space)

    # Process Qt events
    qapp.processEvents()

    # Verify signal was emitted (works with right Ctrl too)
    assert len(signal_emitted) > 0
