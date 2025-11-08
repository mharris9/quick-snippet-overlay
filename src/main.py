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
from src.usage_tracker import UsageTracker

# Configure logging for production (WARNING level - only show warnings and errors)
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

# Lock file path
LOCK_FILE = os.path.abspath(os.path.expanduser("~/.quick-snippet-overlay/app.lock"))


def kill_existing_instances():
    """Kill all existing instances of the application using lock file."""
    killed_count = 0

    # Check if lock file exists
    if not os.path.exists(LOCK_FILE):
        return  # No existing instance

    try:
        # Read PID from lock file
        with open(LOCK_FILE, "r") as f:
            pid = int(f.read().strip())

        logger.info(f"Found existing instance with PID: {pid}")

        # Try to kill the process
        if sys.platform == "win32":
            # Windows: Use taskkill command
            import subprocess
            try:
                # Force kill the process tree
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(pid), "/T"],
                    capture_output=True,
                    timeout=5
                )
                logger.warning(f"Killed existing instance (PID: {pid})")
                killed_count = 1
                import time
                time.sleep(1)  # Wait for process to fully terminate
            except subprocess.TimeoutExpired:
                logger.error(f"Timeout killing process {pid}")
            except Exception as e:
                logger.error(f"Error using taskkill: {e}")
        else:
            # Unix-like: Use os.kill
            try:
                os.kill(pid, 9)  # SIGKILL
                logger.warning(f"Killed existing instance (PID: {pid})")
                killed_count = 1
                import time
                time.sleep(0.5)
            except ProcessLookupError:
                # Process already dead
                logger.info(f"Process {pid} already terminated")
            except Exception as e:
                logger.error(f"Error killing process: {e}")

    except FileNotFoundError:
        # Lock file disappeared, already handled
        pass
    except ValueError:
        # Invalid PID in lock file
        logger.error("Invalid PID in lock file")
    except Exception as e:
        logger.error(f"Error reading lock file: {e}")

    # Always remove the lock file
    if os.path.exists(LOCK_FILE):
        try:
            os.remove(LOCK_FILE)
            logger.info("Removed lock file")
        except Exception as e:
            logger.error(f"Error removing lock file: {e}")

    if killed_count > 0:
        logger.info(f"Killed {killed_count} existing instance(s)")


def ensure_single_instance():
    """Ensure only one instance of application is running."""
    # First, kill any existing instances (also removes lock file)
    kill_existing_instances()

    # Create lock file with current PID
    os.makedirs(os.path.dirname(LOCK_FILE), exist_ok=True)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    logger.info(f"Created lock file with PID: {os.getpid()}")


def is_process_running(pid):
    """Check if a process with given PID is running."""
    if sys.platform == "win32":
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
        snippet_manager = SnippetManager(config_manager.get("snippet_file"))
        snippets = snippet_manager.load()
        search_engine = SearchEngine(snippets)
        variable_handler = VariableHandler()

        # Initialize usage tracker
        usage_stats_file = os.path.join(
            os.path.dirname(config_manager.get("snippet_file")), "usage_stats.yaml"
        )
        usage_tracker = UsageTracker(usage_stats_file)

        # Cleanup orphaned usage stats (remove stats for deleted snippets)
        valid_snippet_ids = [s.id for s in snippets]
        usage_tracker.cleanup_orphaned(valid_snippet_ids)
        usage_tracker.save()

        # Create overlay window (hidden initially)
        overlay_window = OverlayWindow(
            config_manager, snippet_manager, search_engine, variable_handler, usage_tracker
        )

        # Create system tray
        system_tray = SystemTray(overlay_window, snippet_manager, config_manager)

        # Create hotkey manager
        hotkey_string = config_manager.get("hotkey", "ctrl+shift+space")
        hotkey_manager = HotkeyManager(hotkey_string)

        # Connect hotkey to overlay toggle
        def toggle_overlay():
            # Check if a dialog is currently open (editing/deleting)
            if overlay_window.dialog_open:
                # Show notification that editing is in progress
                from PySide6.QtWidgets import QSystemTrayIcon
                if system_tray and system_tray.tray_icon:
                    system_tray.tray_icon.showMessage(
                        "Quick Snippet Overlay",
                        "Please finish editing before using the overlay.",
                        QSystemTrayIcon.MessageIcon.Information,
                        2000  # Show for 2 seconds
                    )
                return

            # Normal toggle behavior
            if overlay_window.isVisible():
                overlay_window.hide_overlay()
            else:
                overlay_window.show_overlay()

        hotkey_manager.hotkey_pressed.connect(toggle_overlay)

        # Start hotkey listener
        hotkey_manager.start()

        # Set up file watcher for auto-reload
        def on_snippets_changed():
            """Callback when snippets file changes."""
            overlay_window.reload_snippets()

        file_observer = snippet_manager.watch_file(on_snippets_changed)

        # Run application event loop
        exit_code = app.exec()

        # Cleanup
        hotkey_manager.stop()
        if file_observer:
            file_observer.stop()
            file_observer.join()

        sys.exit(exit_code)

    except Exception as e:
        logger.error(f"Fatal error during startup: {e}", exc_info=True)
        QMessageBox.critical(
            None, "Startup Error", f"Failed to start Quick Snippet Overlay:\n{str(e)}"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
