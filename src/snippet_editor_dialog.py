"""
Snippet Editor Dialog - Simple GUI for adding snippets

Provides an easy-to-use dialog for creating new snippets without
manually editing YAML files.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit,
    QTextEdit, QPushButton, QLabel, QMessageBox
)
from PySide6.QtCore import Qt


class SnippetEditorDialog(QDialog):
    """Dialog for creating/editing snippets with a simple form."""

    def __init__(self, parent=None):
        """
        Initialize snippet editor dialog.

        Args:
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.snippet_data = None
        self._setup_ui()

    def _setup_ui(self):
        """Create and configure UI components."""
        self.setWindowTitle("Add Snippet")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)

        # Main layout
        layout = QVBoxLayout()

        # Name field
        name_label = QLabel("Name (required):")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("e.g., My Email Signature")
        layout.addWidget(name_label)
        layout.addWidget(self.name_input)

        # Description field
        desc_label = QLabel("Description:")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Brief description for search")
        layout.addWidget(desc_label)
        layout.addWidget(self.desc_input)

        # Tags field
        tags_label = QLabel("Tags (comma-separated):")
        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText("e.g., email, work, signature")
        layout.addWidget(tags_label)
        layout.addWidget(self.tags_input)

        # Content field (multiline)
        content_label = QLabel("Content (required):")
        self.content_input = QTextEdit()
        self.content_input.setPlaceholderText("Paste or type your snippet content here...\n\nTip: Use {{variable_name:default}} for variables")
        layout.addWidget(content_label)
        layout.addWidget(self.content_input)

        # Buttons
        button_layout = QHBoxLayout()

        self.save_button = QPushButton("Save Snippet")
        self.save_button.clicked.connect(self._on_save)
        self.save_button.setDefault(True)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def _on_save(self):
        """Validate and save snippet data."""
        # Get values
        name = self.name_input.text().strip()
        description = self.desc_input.text().strip()
        content = self.content_input.toPlainText().strip()
        tags_str = self.tags_input.text().strip()

        # Validate required fields
        if not name:
            QMessageBox.warning(self, "Validation Error", "Name is required!")
            self.name_input.setFocus()
            return

        if not content:
            QMessageBox.warning(self, "Validation Error", "Content is required!")
            self.content_input.setFocus()
            return

        # Parse and normalize tags
        if tags_str:
            tags = []
            for tag in tags_str.split(','):
                tag = tag.strip()
                if tag:
                    # Normalize: lowercase, replace spaces with dashes
                    normalized_tag = tag.lower().replace(' ', '-')
                    # Remove special characters except hyphens and underscores
                    normalized_tag = ''.join(c for c in normalized_tag if c.isalnum() or c in '-_')
                    if normalized_tag:  # Only add if not empty after normalization
                        tags.append(normalized_tag)
        else:
            tags = []

        # Generate ID from name (lowercase, replace spaces with hyphens)
        snippet_id = name.lower().replace(' ', '-')
        # Remove special characters except hyphens and underscores
        snippet_id = ''.join(c for c in snippet_id if c.isalnum() or c in '-_')

        # Get current timestamp
        today = datetime.now().strftime('%Y-%m-%d')

        # Store snippet data
        self.snippet_data = {
            'id': snippet_id,
            'name': name,
            'description': description if description else name,
            'content': content,
            'tags': tags,
            'created': today,
            'modified': today
        }

        self.accept()

    def get_snippet_data(self):
        """
        Get the snippet data from the dialog.

        Returns:
            Dictionary with snippet fields, or None if cancelled
        """
        return self.snippet_data
