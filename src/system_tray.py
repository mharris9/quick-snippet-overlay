"""
System Tray - System tray icon and context menu for Quick Snippet Overlay

This module provides the system tray icon with a context menu for accessing
application functionality even when the overlay window is hidden.

Classes:
    SystemTray: System tray icon and menu manager
"""

import os
import sys
import logging
from PySide6.QtWidgets import QSystemTrayIcon, QMenu, QApplication, QMessageBox
from PySide6.QtGui import QIcon, QAction


class SystemTray:
    """System tray icon and context menu for Quick Snippet Overlay."""

    def __init__(self, overlay_window, snippet_manager, config_manager):
        """
        Initialize system tray icon.

        Args:
            overlay_window: OverlayWindow instance
            snippet_manager: SnippetManager instance
            config_manager: ConfigManager instance
        """
        self.overlay_window = overlay_window
        self.snippet_manager = snippet_manager
        self.config_manager = config_manager

        # Create tray icon
        self.tray_icon = QSystemTrayIcon()
        self._setup_icon()
        self._setup_menu()

        self.tray_icon.show()
        logging.info("System tray icon created")

    def _setup_icon(self):
        """Set up tray icon and tooltip."""
        icon_path = os.path.join(os.path.dirname(__file__), "icon.png")
        if os.path.exists(icon_path):
            self.tray_icon.setIcon(QIcon(icon_path))
        else:
            # Fallback to built-in Windows application icon
            app = QApplication.instance()
            if app:
                style = app.style()
                icon = style.standardIcon(style.StandardPixmap.SP_ComputerIcon)
                self.tray_icon.setIcon(icon)

        self.tray_icon.setToolTip("Quick Snippet Overlay")

    def _setup_menu(self):
        """Create context menu with actions."""
        menu = QMenu()

        # Open Overlay action
        open_action = QAction("Open Overlay (Ctrl+Shift+Space)", menu)
        open_action.triggered.connect(self._on_open_overlay)
        menu.addAction(open_action)

        # Edit Snippets action
        edit_action = QAction("Edit Snippets (Ctrl+E)", menu)
        edit_action.triggered.connect(self._on_edit_snippets)
        menu.addAction(edit_action)

        # Add Snippet action
        add_snippet_action = QAction("Add Snippet...", menu)
        add_snippet_action.triggered.connect(self._on_add_snippet)
        menu.addAction(add_snippet_action)

        # Reload Snippets action
        reload_action = QAction("Reload Snippets (Ctrl+R)", menu)
        reload_action.triggered.connect(self._on_reload_snippets)
        menu.addAction(reload_action)

        menu.addSeparator()

        # Settings action (placeholder for v1.1)
        settings_action = QAction("Settings...", menu)
        settings_action.setEnabled(False)  # Disabled for v1.0
        menu.addAction(settings_action)

        # About action
        about_action = QAction("About", menu)
        about_action.triggered.connect(self._on_about)
        menu.addAction(about_action)

        menu.addSeparator()

        # Exit action
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(self._on_exit)
        menu.addAction(exit_action)

        self.tray_icon.setContextMenu(menu)

    def _on_open_overlay(self):
        """Handle Open Overlay action."""
        self.overlay_window.show()
        self.overlay_window.activateWindow()
        logging.info("Overlay opened from tray menu")

    def _on_edit_snippets(self):
        """Handle Edit Snippets action - opens YAML file in default editor."""
        snippets_path = self.config_manager.get("snippet_file")
        if sys.platform == "win32":
            os.startfile(snippets_path)
        else:
            os.system(f'xdg-open "{snippets_path}"')
        logging.info(f"Opened snippets file: {snippets_path}")

    def _on_add_snippet(self):
        """Handle Add Snippet action - opens dialog to create new snippet."""
        # Import here to avoid Qt initialization order issues
        from src.snippet_editor_dialog import SnippetEditorDialog

        dialog = SnippetEditorDialog(self.snippet_manager)
        if dialog.exec():
            snippet_data = dialog.get_snippet_data()
            if snippet_data:
                success = self.snippet_manager.add_snippet(snippet_data)
                if success:
                    self.tray_icon.showMessage(
                        "Snippet Added",
                        f"'{snippet_data['name']}' added successfully!",
                        QSystemTrayIcon.MessageIcon.Information,
                        2000,
                    )
                    logging.info(f"Added snippet: {snippet_data['name']}")
                else:
                    QMessageBox.critical(
                        None, "Error", "Failed to save snippet to file."
                    )
                    logging.error("Failed to save snippet")

    def _on_reload_snippets(self):
        """Handle Reload Snippets action."""
        try:
            self.snippet_manager.reload()
            self.tray_icon.showMessage(
                "Snippets Reloaded",
                f"Loaded {len(self.snippet_manager.snippets)} snippets",
                QSystemTrayIcon.MessageIcon.Information,
                2000,  # 2 seconds
            )
            logging.info("Snippets reloaded from tray menu")
        except Exception as e:
            self.tray_icon.showMessage(
                "Reload Failed",
                f"Error: {str(e)}",
                QSystemTrayIcon.MessageIcon.Critical,
                3000,
            )
            logging.error(f"Failed to reload snippets: {e}")

    def _on_about(self):
        """Handle About action."""
        QMessageBox.about(
            None,
            "About Quick Snippet Overlay",
            "Quick Snippet Overlay v1.0.0\n\n"
            "Hotkey-activated text snippet tool for Windows 11.\n\n"
            "Press Ctrl+Shift+Space to open overlay.",
        )

    def _on_exit(self):
        """Handle Exit action - graceful shutdown."""
        logging.info("Exit requested from tray menu")
        QApplication.quit()
