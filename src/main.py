"""
Main - Application entry point for Quick Snippet Overlay

This module provides the application entry point with:
- Single instance enforcement via lock file
- Component initialization and wiring
- Graceful shutdown handling

Functions:
    main: Application entry point
"""

import sys
import os
import logging
import atexit
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt

from src.snippet_manager import SnippetManager
from src.search_engine import SearchEngine
from src.config_manager import ConfigManager
from src.overlay_window import OverlayWindow
from src.system_tray import SystemTray
from src.hotkey_manager import HotkeyManager
from src.variable_handler import VariableHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Lock file path
LOCK_FILE = os.path.abspath(os.path.expanduser('~/.quick-snippet-overlay/app.lock'))


def ensure_single_instance():
    """Ensure only one instance of application is running."""
    if os.path.exists(LOCK_FILE):
        # Check if process still running
        try:
            with open(LOCK_FILE, 'r') as f:
                pid = int(f.read().strip())

            # Check if PID is still running
            if is_process_running(pid):
                QMessageBox.critical(
                    None,
                    "Already Running",
                    "Quick Snippet Overlay is already running.\n"
                    "Check your system tray."
                )
                logging.error(f"Another instance already running (PID: {pid})")
                sys.exit(1)
            else:
                # Stale lock file, remove it
                logging.warning(f"Removing stale lock file (dead PID: {pid})")
                os.remove(LOCK_FILE)
        except Exception as e:
            logging.error(f"Error checking lock file: {e}")
            # Continue anyway

    # Create lock file with current PID
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, 'w') as f:
        f.write(str(os.getpid()))

    logging.info(f"Lock file created: {LOCK_FILE}")


def is_process_running(pid):
    """Check if a process with given PID is running."""
    if sys.platform == 'win32':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        PROCESS_QUERY_INFORMATION = 0x0400
        handle = kernel32.OpenProcess(PROCESS_QUERY_INFORMATION, 0, pid)
        if handle:
            kernel32.CloseHandle(handle)
            return True
        return False
    else:
        # Unix-like
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False


def cleanup_lock_file():
    """Remove lock file on exit."""
    if os.path.exists(LOCK_FILE):
        os.remove(LOCK_FILE)
        logging.info("Lock file removed")


def main():
    """Main entry point for Quick Snippet Overlay."""
    try:
        # Create Qt application FIRST (needed for QMessageBox in single instance check)
        app = QApplication(sys.argv)
        app.setQuitOnLastWindowClosed(False)  # Keep running when overlay closed

        # Ensure single instance
        ensure_single_instance()

        # Register cleanup handler
        atexit.register(cleanup_lock_file)

        # Initialize components
        config_manager = ConfigManager()
        snippet_manager = SnippetManager(config_manager.get('snippet_file'))
        snippets = snippet_manager.load()
        search_engine = SearchEngine(snippets)
        variable_handler = VariableHandler()

        # Create overlay window (hidden initially)
        overlay_window = OverlayWindow(config_manager, snippet_manager, search_engine, variable_handler)

        # Create system tray
        system_tray = SystemTray(overlay_window, snippet_manager, config_manager)

        # Create hotkey manager
        hotkey_string = config_manager.get('hotkey', 'ctrl+shift+space')
        hotkey_manager = HotkeyManager(hotkey_string)

        # Connect hotkey to overlay toggle
        def toggle_overlay():
            if overlay_window.isVisible():
                overlay_window.hide()
            else:
                overlay_window.show()
                overlay_window.activateWindow()

        hotkey_manager.hotkey_pressed.connect(toggle_overlay)

        # Start hotkey listener
        hotkey_manager.start()

        # Set up file watcher for auto-reload
        def on_snippets_changed():
            """Callback when snippets file changes."""
            logging.info("Snippets file changed, reloading...")
            overlay_window.reload_snippets()

        file_observer = snippet_manager.watch_file(on_snippets_changed)

        logging.info("Quick Snippet Overlay started successfully")

        # Run application event loop
        exit_code = app.exec()

        # Cleanup
        hotkey_manager.stop()
        if file_observer:
            file_observer.stop()
            file_observer.join()

        sys.exit(exit_code)

    except Exception as e:
        logging.error(f"Fatal error during startup: {e}", exc_info=True)
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start Quick Snippet Overlay:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == '__main__':
    main()
