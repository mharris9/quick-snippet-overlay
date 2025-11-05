"""
Tests for system_tray.py - System tray icon and context menu

This module tests:
- Tray icon creation and setup
- Context menu creation with all actions
- Menu action handlers (Open, Edit, Reload, About, Exit)
- Integration with overlay window and snippet manager
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock, call
from PySide6.QtWidgets import QApplication, QSystemTrayIcon, QMenu
from PySide6.QtGui import QAction


@pytest.fixture
def qapp():
    """Create Qt application for testing."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def mock_overlay_window():
    """Mock overlay window."""
    overlay = Mock()
    overlay.show = Mock()
    overlay.activateWindow = Mock()
    return overlay


@pytest.fixture
def mock_snippet_manager():
    """Mock snippet manager."""
    manager = Mock()
    manager.reload = Mock()
    manager.snippets = [{'name': 'test1'}, {'name': 'test2'}]
    return manager


@pytest.fixture
def mock_config_manager():
    """Mock config manager."""
    config = Mock()
    config.get = Mock(return_value='C:\\Users\\test\\snippets.yaml')
    return config


def test_tray_icon_creation(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that system tray icon is created and displayed."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Verify tray icon exists
    assert tray.tray_icon is not None
    assert isinstance(tray.tray_icon, QSystemTrayIcon)

    # Verify tooltip is set
    assert tray.tray_icon.toolTip() == "Quick Snippet Overlay"

    # Verify icon is visible
    assert tray.tray_icon.isVisible()


def test_tray_menu_creation(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that context menu is created with all actions."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Get context menu
    menu = tray.tray_icon.contextMenu()
    assert menu is not None
    assert isinstance(menu, QMenu)

    # Get all actions
    actions = menu.actions()
    action_texts = [action.text() for action in actions if not action.isSeparator()]

    # Verify all menu items exist
    assert "Open Overlay" in " ".join(action_texts) or any("Open" in text for text in action_texts)
    assert "Edit Snippets" in " ".join(action_texts) or any("Edit" in text for text in action_texts)
    assert "Reload Snippets" in " ".join(action_texts) or any("Reload" in text for text in action_texts)
    assert "About" in " ".join(action_texts) or any("About" in text for text in action_texts)
    assert "Exit" in " ".join(action_texts) or any("Exit" in text for text in action_texts)


def test_menu_action_open_overlay(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'Open Overlay' action shows the overlay window."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Trigger open overlay action directly
    tray._on_open_overlay()

    # Verify overlay was shown and activated
    mock_overlay_window.show.assert_called_once()
    mock_overlay_window.activateWindow.assert_called_once()


def test_menu_action_edit_snippets(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'Edit Snippets' action opens YAML file in default editor."""
    from src.system_tray import SystemTray

    mock_config_manager.get.return_value = 'C:\\Users\\test\\snippets.yaml'

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Mock os.startfile for Windows
    with patch('os.startfile') as mock_startfile:
        tray._on_edit_snippets()

        # Verify startfile was called with correct path
        mock_startfile.assert_called_once_with('C:\\Users\\test\\snippets.yaml')


def test_menu_action_reload_snippets_success(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'Reload Snippets' action hot-reloads from file successfully."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Mock successful reload
    mock_snippet_manager.snippets = [{'name': 'test1'}, {'name': 'test2'}, {'name': 'test3'}]

    with patch.object(tray.tray_icon, 'showMessage') as mock_show_message:
        tray._on_reload_snippets()

        # Verify reload was called
        mock_snippet_manager.reload.assert_called_once()

        # Verify success message shown
        mock_show_message.assert_called_once()
        call_args = mock_show_message.call_args
        assert "Snippets Reloaded" in call_args[0][0] or "Loaded" in call_args[0][1]


def test_menu_action_reload_snippets_failure(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'Reload Snippets' action handles errors gracefully."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    # Mock failed reload
    mock_snippet_manager.reload.side_effect = Exception("File not found")

    with patch.object(tray.tray_icon, 'showMessage') as mock_show_message:
        tray._on_reload_snippets()

        # Verify error message shown
        mock_show_message.assert_called_once()
        call_args = mock_show_message.call_args
        assert "Reload Failed" in call_args[0][0] or "Error" in call_args[0][1] or "Failed" in call_args[0][1]


def test_menu_action_about(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'About' action shows version information."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    with patch('PySide6.QtWidgets.QMessageBox.about') as mock_about:
        tray._on_about()

        # Verify about dialog was shown
        mock_about.assert_called_once()

        # Verify version info in message
        call_args = mock_about.call_args[0]
        message = call_args[2]
        assert "v1.0.0" in message or "1.0.0" in message
        assert "Quick Snippet Overlay" in message


def test_menu_action_exit(qapp, mock_overlay_window, mock_snippet_manager, mock_config_manager):
    """Test that 'Exit' action triggers graceful shutdown."""
    from src.system_tray import SystemTray

    tray = SystemTray(mock_overlay_window, mock_snippet_manager, mock_config_manager)

    with patch('PySide6.QtWidgets.QApplication.quit') as mock_quit:
        tray._on_exit()

        # Verify QApplication.quit was called
        mock_quit.assert_called_once()
