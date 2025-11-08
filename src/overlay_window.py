"""
Overlay Window - Main UI for searching and selecting snippets

This module provides the frameless, always-on-top overlay window that allows
users to search for snippets, navigate with keyboard, and copy to clipboard.

Classes:
    OverlayWindow: Main overlay window with search and results display
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)

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
    QMenu,
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

    def __init__(self, config, snippet_manager, search_engine, variable_handler, usage_tracker):
        """
        Initialize overlay window.

        Args:
            config: ConfigManager instance
            snippet_manager: SnippetManager instance
            search_engine: SearchEngine instance
            variable_handler: VariableHandler instance
            usage_tracker: UsageTracker instance for frequency tracking
        """
        super().__init__()
        self.config = config
        self.snippet_manager = snippet_manager
        self.search_engine = search_engine
        self.variable_handler = variable_handler
        self.usage_tracker = usage_tracker

        self.debounce_timer = None
        self.copied_label = None

        # For drag functionality
        self.drag_position = None

        # Track if dialog is open (prevents hotkey toggle during editing)
        self.dialog_open = False

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

        # Edit snippet button
        self.edit_button = QPushButton("✏️")
        self.edit_button.setToolTip("Edit Selected Snippet")
        self.edit_button.setFixedSize(40, 40)
        self.edit_button.clicked.connect(self._on_edit_snippet_clicked)
        self.edit_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
            QPushButton:pressed {
                background-color: #E65100;
            }
        """
        )
        top_layout.addWidget(self.edit_button)

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
        # Enable context menu on right-click
        self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
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
        self.results_list.customContextMenuRequested.connect(self._show_context_menu)

    def show_overlay(self):
        """Show overlay and focus search box, centered on active monitor."""
        # Block signals to prevent textChanged from interfering
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)

        self.results_list.clear()

        # Show all snippets alphabetically (no filter)
        self._update_results("")

        # Show window first
        self.show()

        # Defer centering until after event loop processes show()
        QTimer.singleShot(0, self._center_on_active_monitor)

        # Defer focus/activation to ensure window is positioned first
        # This ensures popup "click outside to close" works immediately
        QTimer.singleShot(10, self._activate_and_focus)

    def _activate_and_focus(self):
        """Activate window and set focus (ensures popup click-outside behavior works)."""
        self.raise_()  # Raise window to top of window stack
        self.activateWindow()  # Activate the window
        self.search_input.setFocus()  # Set focus to search input

    def _center_on_active_monitor(self):
        """Center window on the active monitor (called after show)."""
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

            # Calculate center position
            x = screen_geometry.x() + (screen_geometry.width() - self.width()) // 2
            y = screen_geometry.y() + (screen_geometry.height() - self.height()) // 2

            self.move(x, y)

    def hide_overlay(self):
        """Hide overlay and clear state."""
        self.hide()
        # Block signals to prevent textChanged events
        self.search_input.blockSignals(True)
        self.search_input.clear()
        self.search_input.blockSignals(False)
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
            logger.error(f"Failed to reload snippets: {e}")

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

        max_results = self.config.get("max_results", 10)

        if not query.strip():
            # Empty search: show all snippets sorted by frequency then alphabetically
            sorted_snippets = self.snippet_manager.get_sorted_snippets(self.usage_tracker)
            limited_snippets = sorted_snippets[:max_results]

            # Display snippets
            for snippet in limited_snippets:
                # Truncate content to 2 lines
                content_lines = snippet.content.split("\n")
                truncated = "\n".join(content_lines[:2])
                if len(content_lines) > 2:
                    truncated += "\n..."

                # Create list item
                item = QListWidgetItem()
                item.setText(f"{snippet.name}\n{truncated}")
                item.setData(Qt.ItemDataRole.UserRole, snippet)
                self.results_list.addItem(item)
        else:
            # Search snippets with fuzzy matching
            threshold = self.config.get("fuzzy_threshold", 60)
            results = self.search_engine.search(query, threshold=threshold)

            # Sort results by usage frequency (most used first), then by search score
            # Get usage counts for sorting
            def sort_key(result):
                snippet = result["snippet"]
                usage_count = self.usage_tracker.get_count(snippet.id)
                search_score = result["score"]
                # Primary: usage frequency (descending), Secondary: search score (descending)
                return (-usage_count, -search_score)

            results.sort(key=sort_key)

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

            # Increment usage count and save
            self.usage_tracker.increment(snippet.id)
            self.usage_tracker.save()

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

        # Mark dialog as open (prevents hotkey toggle)
        self.dialog_open = True

        try:
            # Create and show dialog
            dialog = SnippetEditorDialog(
                snippet_manager=self.snippet_manager,
                parent=self,  # Overlay as parent for proper stacking
            )

            # Show dialog modally
            result = dialog.exec()

            # If snippet was saved, add it to the YAML file
            if result == QDialog.DialogCode.Accepted:
                snippet_data = dialog.get_snippet_data()
                if snippet_data:
                    # Save to YAML file
                    success = self.snippet_manager.add_snippet(snippet_data)
                    if success:
                        # Reload snippets from file
                        self.reload_snippets()
                        # Refresh overlay results
                        self._update_results(self.search_input.text())
                    else:
                        QMessageBox.warning(
                            self, "Error", "Failed to save snippet to file."
                        )

            # Restore focus to search input
            self.search_input.setFocus()

        finally:
            # Always reset dialog flag when dialog closes
            self.dialog_open = False

    def _on_edit_snippet_clicked(self):
        """Open the Edit Snippet dialog for the currently selected snippet."""
        from src.snippet_editor_dialog import SnippetEditorDialog
        from PySide6.QtWidgets import QDialog

        # Get currently selected item
        current_item = self.results_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self, "No Selection", "Please select a snippet to edit."
            )
            return

        # Get the snippet object from the item
        snippet = current_item.data(Qt.ItemDataRole.UserRole)
        if not snippet:
            return

        # Mark dialog as open (prevents hotkey toggle)
        self.dialog_open = True

        try:
            # Create and show dialog in edit mode
            dialog = SnippetEditorDialog(
                snippet_manager=self.snippet_manager,
                parent=self,
                snippet=snippet,  # Pass the snippet for editing
            )

            # Show dialog modally
            result = dialog.exec()

            # If snippet was saved, update it in the YAML file
            if result == QDialog.DialogCode.Accepted:
                snippet_data = dialog.get_snippet_data()
                if snippet_data:
                    # Update snippet in YAML file
                    success = self.snippet_manager.update_snippet(
                        snippet.id, snippet_data
                    )
                    if success:
                        # Reload snippets from file
                        self.reload_snippets()
                        # Refresh overlay results
                        self._update_results(self.search_input.text())
                    else:
                        QMessageBox.warning(
                            self, "Error", "Failed to update snippet in file."
                        )

            # Restore focus to search input
            self.search_input.setFocus()

        finally:
            # Always reset dialog flag when dialog closes
            self.dialog_open = False

    def _on_delete_snippets_clicked(self):
        """Open the Delete Snippets dialog."""
        from src.delete_snippets_dialog import DeleteSnippetsDialog
        from PySide6.QtWidgets import QDialog

        # Mark dialog as open (prevents hotkey toggle)
        self.dialog_open = True

        try:
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

        finally:
            # Always reset dialog flag when dialog closes
            self.dialog_open = False

    def _show_context_menu(self, position):
        """Show context menu on right-click with Edit and Delete options."""
        logger.info(f"Context menu requested at position: {position}")

        # Get item at position
        item = self.results_list.itemAt(position)
        if not item:
            logger.warning("No item at position, returning")
            return

        logger.info(f"Item found: {item.text()[:30]}")

        # Don't show menu if dialog is open
        if self.dialog_open:
            logger.warning("Dialog is open, not showing context menu")
            return

        # Select the item (if not already selected)
        self.results_list.setCurrentItem(item)

        # Create menu
        menu = QMenu(self)
        edit_action = menu.addAction("Edit")
        delete_action = menu.addAction("Delete")

        # Connect actions
        edit_action.triggered.connect(self._on_edit_snippet_clicked)
        delete_action.triggered.connect(self._on_delete_single_snippet)

        # Show menu at cursor position
        menu.exec(self.results_list.mapToGlobal(position))

    def _on_delete_single_snippet(self):
        """Delete the currently selected snippet via context menu."""
        current_item = self.results_list.currentItem()
        if not current_item:
            return

        snippet = current_item.data(Qt.ItemDataRole.UserRole)
        if not snippet:
            return

        # Mark dialog as open
        self.dialog_open = True

        try:
            # Show confirmation
            reply = QMessageBox.question(
                self,
                "Delete Snippet",
                f"Are you sure you want to delete '{snippet.name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No,
            )

            if reply == QMessageBox.StandardButton.Yes:
                # Delete the snippet
                self.snippet_manager.delete_snippets([snippet.id])

                # Reload and refresh
                self.reload_snippets()
                self._update_results(self.search_input.text())
        finally:
            self.dialog_open = False
