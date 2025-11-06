"""
Delete Snippets Dialog - Mass snippet deletion with filtering

This module provides a dialog for selecting and deleting multiple snippets
with filtering capabilities.

Classes:
    SnippetCheckboxItem: QWidget for snippet with checkbox
    DeleteSnippetsDialog: Main deletion dialog
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QWidget,
    QCheckBox,
    QLabel,
    QMessageBox,
    QListWidget,
    QListWidgetItem,
)
from PySide6.QtCore import Qt, QTimer
from typing import List
from src.snippet_manager import Snippet


class SnippetCheckboxItem(QWidget):
    """
    Widget representing a single snippet with checkbox.

    Contains:
    - Checkbox
    - Snippet name (large, bold)
    - Snippet tags (smaller, gray)
    - Snippet created date (smaller, gray)
    """

    def __init__(self, snippet: Snippet, parent=None):
        super().__init__(parent)
        self.snippet = snippet
        self.checkbox = QCheckBox()
        self._setup_ui()

    def _setup_ui(self):
        """Create UI components."""
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)

        # Checkbox
        self.checkbox.setChecked(False)
        layout.addWidget(self.checkbox)

        # Text layout (vertical)
        text_layout = QVBoxLayout()

        # Name label (bold, 14pt)
        name_label = QLabel(self.snippet.name)
        name_label.setStyleSheet("font-size: 14pt; font-weight: bold;")
        text_layout.addWidget(name_label)

        # Tags and date (gray, 10pt)
        tags_str = ", ".join(self.snippet.tags) if self.snippet.tags else "No tags"
        meta_label = QLabel(f"Tags: {tags_str} | Created: {self.snippet.created}")
        meta_label.setStyleSheet("color: #888888; font-size: 10pt;")
        text_layout.addWidget(meta_label)

        layout.addLayout(text_layout)
        layout.addStretch()

        self.setLayout(layout)

    def is_checked(self) -> bool:
        """Return whether checkbox is checked."""
        return self.checkbox.isChecked()

    def set_checked(self, checked: bool):
        """Set checkbox state."""
        self.checkbox.setChecked(checked)

    def matches_filter(self, filter_text: str) -> bool:
        """Check if snippet matches filter text."""
        filter_lower = filter_text.lower()
        return (
            filter_lower in self.snippet.name.lower()
            or filter_lower in self.snippet.description.lower()
            or any(filter_lower in tag.lower() for tag in self.snippet.tags)
            or filter_lower in self.snippet.content.lower()
        )


class DeleteSnippetsDialog(QDialog):
    """
    Dialog for deleting snippets with filtering and mass selection.

    Features:
    - Filter snippets by name/tags/content
    - Select/deselect all (filtered)
    - Mass delete with confirmation
    - Real-time selection count
    """

    def __init__(self, snippets: List[Snippet], snippet_manager, parent=None):
        super().__init__(parent)
        self.snippets = snippets
        self.snippet_manager = snippet_manager
        self.snippet_items = []  # List of SnippetCheckboxItem widgets
        self.filter_text = ""
        self.debounce_timer = None

        self._setup_ui()
        self._populate_snippets()
        self._update_selection_count()

    def _setup_ui(self):
        """Create dialog UI."""
        self.setWindowTitle("Delete Snippets")
        self.setMinimumSize(600, 500)

        layout = QVBoxLayout()

        # Filter section
        filter_layout = QHBoxLayout()

        self.filter_input = QLineEdit()
        self.filter_input.setPlaceholderText(
            "Filter snippets by name, tags, or content..."
        )
        self.filter_input.textChanged.connect(self._on_filter_changed)
        filter_layout.addWidget(self.filter_input)

        clear_button = QPushButton("Clear")
        clear_button.clicked.connect(self._clear_filter)
        filter_layout.addWidget(clear_button)

        layout.addLayout(filter_layout)

        # Select All checkbox
        self.select_all_checkbox = QCheckBox("Select All")
        self.select_all_checkbox.stateChanged.connect(self._on_select_all_changed)
        layout.addWidget(self.select_all_checkbox)

        # Scroll area for snippet list
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.snippet_container = QWidget()
        self.snippet_layout = QVBoxLayout()
        self.snippet_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.snippet_container.setLayout(self.snippet_layout)

        scroll_area.setWidget(self.snippet_container)
        layout.addWidget(scroll_area)

        # Selection count label
        self.selection_label = QLabel("0 snippets selected")
        layout.addWidget(self.selection_label)

        # Buttons
        button_layout = QHBoxLayout()

        self.delete_button = QPushButton("Delete Selected (0)")
        self.delete_button.setStyleSheet(
            """
            QPushButton {
                background-color: #d32f2f;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c62828;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        )
        self.delete_button.clicked.connect(self._on_delete_clicked)
        self.delete_button.setEnabled(False)
        button_layout.addWidget(self.delete_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Apply dark theme
        self._apply_theme()

    def _apply_theme(self):
        """Apply dark theme styling."""
        dark_theme = """
        QDialog {
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
        QScrollArea {
            background-color: #3c3c3c;
            border: 1px solid #555555;
            border-radius: 5px;
        }
        QCheckBox {
            color: #ffffff;
        }
        QLabel {
            color: #ffffff;
        }
        """
        self.setStyleSheet(dark_theme)

    def keyPressEvent(self, event):
        """Handle keyboard events (Escape to close)."""
        from PySide6.QtGui import QKeyEvent
        from PySide6.QtCore import Qt

        if event.key() == Qt.Key.Key_Escape:
            # Close dialog without deleting
            self.reject()
            event.accept()
        else:
            # Pass other keys to parent handler
            super().keyPressEvent(event)

    def _populate_snippets(self):
        """Populate snippet list with checkbox items."""
        # Clear existing items
        for item in self.snippet_items:
            self.snippet_layout.removeWidget(item)
            item.deleteLater()
        self.snippet_items.clear()

        # Add snippet items
        for snippet in self.snippets:
            item = SnippetCheckboxItem(snippet)
            item.checkbox.stateChanged.connect(self._on_checkbox_changed)

            # Apply filter if active
            if self.filter_text and not item.matches_filter(self.filter_text):
                item.hide()
            else:
                item.show()

            self.snippet_layout.addWidget(item)
            self.snippet_items.append(item)

    def _on_filter_changed(self, text: str):
        """Handle filter input change with debouncing."""
        # Cancel previous timer
        if self.debounce_timer:
            self.debounce_timer.stop()

        # Create new debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.setSingleShot(True)
        self.debounce_timer.timeout.connect(lambda: self._apply_filter(text))
        self.debounce_timer.start(150)

    def _apply_filter(self, text: str):
        """Apply filter to snippet list."""
        self.filter_text = text

        # Show/hide items based on filter
        for item in self.snippet_items:
            if not text or item.matches_filter(text):
                item.show()
            else:
                item.hide()

        self._update_selection_count()

    def _clear_filter(self):
        """Clear filter and show all snippets."""
        self.filter_input.clear()
        self.filter_text = ""

        for item in self.snippet_items:
            item.show()

        self._update_selection_count()

    def _on_select_all_changed(self, state):
        """Handle Select All checkbox change."""
        checked = state == Qt.CheckState.Checked.value

        # Toggle all visible items
        for item in self.snippet_items:
            if item.isVisible():
                item.set_checked(checked)

        self._update_selection_count()

    def _on_checkbox_changed(self):
        """Handle individual checkbox change."""
        self._update_selection_count()

    def _update_selection_count(self):
        """Update selection count label and button state."""
        selected_count = sum(1 for item in self.snippet_items if item.is_checked())

        self.selection_label.setText(f"{selected_count} snippet(s) selected")
        self.delete_button.setText(f"Delete Selected ({selected_count})")
        self.delete_button.setEnabled(selected_count > 0)

    def _on_delete_clicked(self):
        """Handle delete button click."""
        # Get selected snippets
        selected_snippets = [
            item.snippet for item in self.snippet_items if item.is_checked()
        ]

        if not selected_snippets:
            return

        # Show confirmation dialog
        confirmed = self._show_confirmation_dialog(selected_snippets)

        if confirmed:
            # Delete snippets
            self._delete_snippets(selected_snippets)

            # Accept dialog (trigger refresh in overlay)
            self.accept()

    def _show_confirmation_dialog(self, snippets: List[Snippet]) -> bool:
        """
        Show confirmation dialog for deletion.

        Returns:
            True if user confirmed, False otherwise
        """
        count = len(snippets)

        # Build snippet list for message
        snippet_names = "\n".join([f"• {s.name}" for s in snippets[:10]])
        if count > 10:
            snippet_names += f"\n... and {count - 10} more"

        message = (
            f"Are you sure you want to delete {count} snippet(s)?\n\n"
            f"This action cannot be undone.\n\n"
            f"Snippets to be deleted:\n{snippet_names}"
        )

        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,  # Default to No (safe)
        )

        return reply == QMessageBox.StandardButton.Yes

    def _delete_snippets(self, snippets: List[Snippet]):
        """
        Delete snippets from snippet manager.

        Args:
            snippets: List of Snippet objects to delete
        """
        try:
            # Get snippet IDs
            snippet_ids = [s.id for s in snippets]

            # Call snippet_manager to delete
            self.snippet_manager.delete_snippets(snippet_ids)

            # Show success message
            QMessageBox.information(
                self, "Success", f"Successfully deleted {len(snippets)} snippet(s)."
            )
        except Exception as e:
            # Show error message
            QMessageBox.critical(self, "Error", f"Failed to delete snippets: {str(e)}")
