"""
Overlay Window - Main UI for searching and selecting snippets

This module provides the frameless, always-on-top overlay window that allows
users to search for snippets, navigate with keyboard, and copy to clipboard.

Classes:
    OverlayWindow: Main overlay window with search and results display
"""

from typing import Optional
import logging
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QListWidget,
    QLabel,
    QListWidgetItem,
    QMessageBox,
    QApplication,
    QPushButton,
)
from PySide6.QtCore import Qt, QTimer, QCoreApplication
from PySide6.QtGui import QCursor, QKeyEvent
import pyperclip

from src.variable_prompt_dialog import prompt_for_variables


class OverlayWindow(QWidget):
    """
    Main overlay window for searching and selecting snippets.

    Features:
    - Frameless, always-on-top window
    - Real-time search with debouncing
    - Keyboard navigation (arrows, Enter, ESC)
    - Multi-monitor support (centers on active monitor)
    - Variable prompt integration
    - Clipboard copy with visual feedback
    - Quick add snippet button (+ button or Ctrl+N)
    """

    def __init__(self, config, snippet_manager, search_engine, variable_handler):
        """
        Initialize overlay window.

        Args:
            config: ConfigManager instance
            snippet_manager: SnippetManager instance
            search_engine: SearchEngine instance
            variable_handler: VariableHandler instance
        """
        super().__init__()
        self.config = config
        self.snippet_manager = snippet_manager
        self.search_engine = search_engine
        self.variable_handler = variable_handler

        self.debounce_timer = None
        self.copied_label = None

        # For drag functionality
        self.drag_position = None

        self._setup_ui()
        self._setup_connections()

    def _setup_ui(self):
        """Create and configure UI components."""
        # Window flags: frameless, always-on-top, popup (auto-close and escape work)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Popup
        )

        # Attribute to prevent auto-close during drag
        self.setAttribute(Qt.WidgetAttribute.WA_NoMousePropagation, False)

        # Size and opacity from config
        width = self.config.get("overlay_width", 600)
        height = self.config.get("overlay_height", 400)
        self.setFixedSize(width, height)

        opacity = self.config.get("overlay_opacity", 0.95)
        self.setWindowOpacity(opacity)

        # Main layout
        layout = QVBoxLayout()

        # Top layout: search input + add button
        top_layout = QHBoxLayout()

        # Search input (40px height, 16pt font)
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search snippets...")
        self.search_input.setFixedHeight(40)
        font = self.search_input.font()
        font.setPointSize(16)
        self.search_input.setFont(font)
        top_layout.addWidget(self.search_input)

        # Delete snippets button
        self.delete_button = QPushButton("🗑️")
        self.delete_button.setToolTip("Delete Snippets (Ctrl+D)")
        self.delete_button.setFixedSize(40, 40)
        self.delete_button.clicked.connect(self._on_delete_snippets_clicked)
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d32f2f;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
        """
        )
        top_layout.addWidget(self.delete_button)

        # Add snippet button
        self.add_button = QPushButton("+")
        self.add_button.setToolTip("Add New Snippet (Ctrl+N)")
        self.add_button.setFixedSize(40, 40)
        self.add_button.clicked.connect(self._on_add_snippet_clicked)
        self.add_button.setStyleSheet(
            """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """
        )
        top_layout.addWidget(self.add_button)

        layout.addLayout(top_layout)

        # Results list (scrollable)
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)

        # "Copied!" feedback label (initially hidden)
        self.copied_label = QLabel("Copied!")
        self.copied_label.setStyleSheet(
            "color: green; font-weight: bold; font-size: 14pt;"
        )
        self.copied_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.copied_label.hide()
        layout.addWidget(self.copied_label)

        self.setLayout(layout)

        # Apply dark theme
        self._apply_theme()

    def _apply_theme(self):
        """Apply dark theme styling."""
        theme = self.config.get("theme", "dark")

        if theme == "dark":
            dark_theme = """
            QWidget {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLineEdit {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                padding: 5px;
                border-radius: 5px;
                color: #ffffff;
            }
            QListWidget {
                background-color: #3c3c3c;
                border: 1px solid #555555;
                border-radius: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #0078d4;
            }
            """
            self.setStyleSheet(dark_theme)

    def _setup_connections(self):
        """Connect signals to slots."""
        self.search_input.textChanged.connect(self._on_search_input_changed)
        self.results_list.itemDoubleClicked.connect(self._on_snippet_selected)

    def show_overlay(self):
        """Show overlay and focus search box, centered on active monitor."""
        # Clear state first
        self.search_input.clear()
        self.results_list.clear()

        # Get active screen (monitor with mouse cursor)
        cursor_pos = QCursor.pos()
        app = QApplication.instance()

        # Get screen at cursor position
        active_screen = None
        if app:
            active_screen = app.screenAt(cursor_pos)

        if active_screen is None:
            # Fallback to primary screen
            if app:
                active_screen = app.primaryScreen()

        # Center on active screen
        if active_screen:
            screen_geometry = active_screen.availableGeometry()
            x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2
            self.move(x, y)

        # Show window and focus search input
        self.show()
        self.activateWindow()
        self.search_input.setFocus()

    def hide_overlay(self):
        """Hide overlay and clear state."""
        self.hide()
        self.search_input.clear()
        self.results_list.clear()

    def reload_snippets(self):
        """Reload snippets from file and update search engine."""
        try:
            snippets = self.snippet_manager.load()
            # Update search engine with new snippets
            from src.search_engine import SearchEngine

            self.search_engine = SearchEngine(snippets)
            # If overlay is visible, refresh search results
            if self.isVisible():
                self._perform_search()
        except Exception as e:
            logging.error(f"Failed to reload snippets: {e}")

    def _on_search_input_changed(self, text):
        """Handle search input change with debouncing."""
        # Cancel previous timer if exists
        if self.debounce_timer:
            self.debounce_timer.stop()

        # Create new debounce timer
        debounce_ms = self.config.get("search_debounce_ms", 150)
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(lambda: self._update_results(text))
        self.debounce_timer.start(debounce_ms)

    def _update_results(self, query):
        """Update results list based on search query."""
        self.results_list.clear()

        if not query.strip():
            # Empty search: show nothing
            return

        # Search snippets
        max_results = self.config.get("max_results", 10)
        threshold = self.config.get("fuzzy_threshold", 60)

        results = self.search_engine.search(query, threshold=threshold)

        # Limit results to max_results
        limited_results = results[:max_results]

        # Display results with truncation
        for result in limited_results:
            snippet = result["snippet"]

            # Truncate content to 2 lines
            content_lines = snippet.content.split("\n")
            truncated = "\n".join(content_lines[:2])
            if len(content_lines) > 2:
                truncated += "\n..."

            # Create list item
            item = QListWidgetItem()
            item.setText(f"{snippet.name}\n{truncated}")
            item.setData(Qt.ItemDataRole.UserRole, snippet)  # Store snippet object
            self.results_list.addItem(item)

        # Select first result
        if self.results_list.count() > 0:
            self.results_list.setCurrentRow(0)

    def keyPressEvent(self, event: QKeyEvent):
        """Handle keyboard events (Ctrl+N, Ctrl+D, Enter, ESC, arrows)."""
        # Ctrl+N to add new snippet
        if (
            event.key() == Qt.Key.Key_N
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._on_add_snippet_clicked()
            event.accept()
            return
        # Ctrl+D to delete snippets
        elif (
            event.key() == Qt.Key.Key_D
            and event.modifiers() == Qt.KeyboardModifier.ControlModifier
        ):
            self._on_delete_snippets_clicked()
            event.accept()
            return
        elif event.key() == Qt.Key.Key_Escape:
            self.hide_overlay()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self._on_snippet_selected()
        elif event.key() == Qt.Key.Key_Down:
            current = self.results_list.currentRow()
            max_row = self.results_list.count() - 1
            if current < max_row:
                self.results_list.setCurrentRow(current + 1)
        elif event.key() == Qt.Key.Key_Up:
            current = self.results_list.currentRow()
            if current > 0:
                self.results_list.setCurrentRow(current - 1)
        else:
            super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse press for dragging window."""
        if event.button() == Qt.MouseButton.LeftButton:
            # Record starting position for drag
            try:
                self.drag_position = (
                    event.globalPosition().toPoint() - self.frameGeometry().topLeft()
                )
            except AttributeError:
                self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging window."""
        if (
            event.buttons() == Qt.MouseButton.LeftButton
            and self.drag_position is not None
        ):
            try:
                new_pos = event.globalPosition().toPoint() - self.drag_position
            except AttributeError:
                new_pos = event.globalPos() - self.drag_position
            self.move(new_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        """Handle mouse release to end dragging."""
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = None
            event.accept()

    def _on_snippet_selected(self):
        """Handle snippet selection (Enter key or double-click)."""
        current_item = self.results_list.currentItem()
        if not current_item:
            return

        snippet = current_item.data(Qt.ItemDataRole.UserRole)
        self._copy_snippet_to_clipboard(snippet)

    def _copy_snippet_to_clipboard(self, snippet):
        """Copy snippet to clipboard (with variable substitution if needed)."""
        content = snippet.content

        # Check for variables
        variables = self.variable_handler.detect_variables(content)

        if variables:
            # Show sequential prompts
            values = prompt_for_variables(variables, parent=self)
            if values is None:
                # User cancelled, return to overlay without closing
                return

            # Substitute variables
            try:
                content = self.variable_handler.substitute_variables(content, values)
            except ValueError as e:
                QMessageBox.warning(self, "Error", f"Variable substitution failed: {e}")
                return

        # Copy to clipboard
        try:
            pyperclip.copy(content)
            self._show_copied_feedback()

            # Close overlay after 500ms
            QTimer.singleShot(500, self.hide_overlay)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Unable to copy to clipboard: {e}")

    def _show_copied_feedback(self):
        """Show brief 'Copied!' message."""
        self.copied_label.show()
        QTimer.singleShot(500, self.copied_label.hide)

    def _on_add_snippet_clicked(self):
        """Open the Add Snippet dialog."""
        from src.snippet_editor_dialog import SnippetEditorDialog
        from PySide6.QtWidgets import QDialog

        # Create and show dialog
        dialog = SnippetEditorDialog(
            snippet_manager=self.snippet_manager,
            parent=self,  # Overlay as parent for proper stacking
        )

        # Show dialog modally
        result = dialog.exec()

        # If snippet was saved, refresh the overlay results
        if result == QDialog.DialogCode.Accepted:
            # Reload snippets (snippet_manager watches file, but force refresh)
            self._update_results(self.search_input.text())

            # Restore focus to search input
            self.search_input.setFocus()

    def _on_delete_snippets_clicked(self):
        """Open the Delete Snippets dialog."""
        from src.delete_snippets_dialog import DeleteSnippetsDialog
        from PySide6.QtWidgets import QDialog

        # Get all snippets from snippet_manager
        snippets = self.snippet_manager.get_all_snippets()

        # IMPORTANT: Hide the overlay before showing the dialog
        # This prevents keyboard/focus conflicts with the Popup window
        self.hide()

        # Create and show dialog (parent=None to make it independent)
        dialog = DeleteSnippetsDialog(
            snippets=snippets, snippet_manager=self.snippet_manager, parent=None
        )

        # Show dialog modally
        result = dialog.exec()

        # Don't automatically show the overlay again - user can reopen with hotkey
        # This prevents the overlay from interfering with other applications
