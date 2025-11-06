"""
Snippet Editor Dialog - Simple GUI for adding snippets

Provides an easy-to-use dialog for creating new snippets without
manually editing YAML files.
"""

from datetime import datetime
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QMessageBox,
    QListView,
)
from PySide6.QtCore import Qt, QTimer, QObject, QEvent
from src.fuzzy_tag_completer import FuzzyTagCompleter


class NoFocusListView(QListView):
    """Custom QListView that refuses to accept focus, preventing focus stealing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # TEST #4: Disable keyboard interaction entirely
        self.setFocusProxy(None)

    def focusInEvent(self, event):
        """
        Override to accept focus events without taking focus.
        event.accept() tells Qt we handled it, preventing view from taking focus.
        """
        event.accept()
        # Don't call super() - this prevents the view from actually taking focus

    def focusOutEvent(self, event):
        """Override to accept focus out events."""
        event.accept()

    def keyPressEvent(self, event):
        """
        Reject ALL keyboard events - they should go to tags_input instead.
        The popup should NEVER handle keyboard input.
        """
        event.ignore()
        # Don't call super() - this prevents the popup from handling the key

    def event(self, event):
        """Override event() to reject activation events that steal keyboard routing."""
        # Reject keyboard events - they should go to tags_input
        if event.type() in [
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
            QEvent.Type.ShortcutOverride,
            QEvent.Type.InputMethod,
        ]:
            event.ignore()
            return False  # Don't handle it

        # Reject window activation events (these steal keyboard routing!)
        if event.type() in [
            QEvent.Type.WindowActivate,
            QEvent.Type.ActivationChange,
            QEvent.Type.FocusIn,
        ]:
            event.ignore()
            return False  # Don't handle activation

        # Allow all other events (including mouse clicks) to proceed normally
        return super().event(event)


class InputFocusProtector(QObject):
    """Event filter that prevents the tags input field from losing focus to the popup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.popup = None  # Will be set by SnippetEditorDialog
        self.completion_handler = None  # Will be set to _on_completion_selected

    def eventFilter(self, obj, event):
        """
        Block FocusOut events when popup is visible to keep focus in input field.
        Also handle ESC key to dismiss popup and focus changes.

        Args:
            obj: The object being filtered (tags_input)
            event: The event to filter

        Returns:
            bool: True to block the event, False to allow it
        """
        # Handle keyboard events
        if event.type() == QEvent.Type.KeyPress:
            key = event.key()

            # ESC key dismisses popup
            if key == Qt.Key.Key_Escape and self.popup and self.popup.isVisible():
                self.popup.hide()
                return True  # Consume the ESC event

            # Tab key auto-completes with first item in list
            if key == Qt.Key.Key_Tab and self.popup and self.popup.isVisible():
                # Get the first item from the popup's model
                model = self.popup.model()
                if model and model.rowCount() > 0:
                    first_index = model.index(0, 0)
                    first_item = model.data(first_index, Qt.ItemDataRole.DisplayRole)
                    if first_item and self.completion_handler:
                        # Trigger the selection handler
                        self.completion_handler(first_item)
                        return True  # Consume the Tab event

            # Enter/Return key selects highlighted item (if any) or first item
            if (
                key in [Qt.Key.Key_Return, Qt.Key.Key_Enter]
                and self.popup
                and self.popup.isVisible()
            ):
                # Try to get currently selected item
                current_index = self.popup.currentIndex()
                model = self.popup.model()
                if current_index.isValid() and model:
                    selected_item = model.data(
                        current_index, Qt.ItemDataRole.DisplayRole
                    )
                    if selected_item and self.completion_handler:
                        self.completion_handler(selected_item)
                        return True  # Consume the Enter event

        if event.type() == QEvent.Type.FocusOut:
            # Hide popup when focus leaves tags_input (moving to another field)
            focus_widget = obj.window().focusWidget()

            # If focus is going to the popup, block it (keep focus on tags_input)
            if focus_widget and isinstance(focus_widget, NoFocusListView):
                return True

            # If focus is going to another widget (name, description, buttons), hide popup
            if self.popup and self.popup.isVisible():
                self.popup.hide()

        return False


class SnippetEditorDialog(QDialog):
    """Dialog for creating/editing snippets with a simple form."""

    def __init__(self, snippet_manager=None, parent=None):
        """
        Initialize snippet editor dialog.

        Args:
            snippet_manager: SnippetManager instance for tag suggestions (optional)
            parent: Parent widget (optional)
        """
        super().__init__(parent)
        self.snippet_manager = snippet_manager
        self.snippet_data = None
        self._setup_ui()
        self._setup_completer()

    def mousePressEvent(self, event):
        """
        Handle mouse clicks on the dialog.
        Hide popup if clicking outside of tags_input and popup.
        """
        if hasattr(self, "fuzzy_completer"):
            popup = self.fuzzy_completer.popup()
            if popup and popup.isVisible():
                # Check if click is outside tags_input - hide popup
                if not self.tags_input.geometry().contains(event.pos()):
                    popup.hide()
        super().mousePressEvent(event)

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
        self.content_input.setPlaceholderText(
            "Paste or type your snippet content here...\n\nTip: Use {{variable_name:default}} for variables"
        )
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

    def _setup_completer(self):
        """Setup fuzzy autocomplete for tag input field."""
        if not self.snippet_manager:
            return

        self.all_tags = self.snippet_manager.get_all_tags()

        # Use FuzzyTagCompleter for typo-tolerant suggestions
        self.fuzzy_completer = FuzzyTagCompleter(self.all_tags, self)

        # PopupCompletion (NOT Unfiltered) to prevent inline auto-completion
        self.fuzzy_completer.setCompletionMode(
            self.fuzzy_completer.CompletionMode.PopupCompletion
        )
        self.fuzzy_completer.setMaxVisibleItems(10)
        self.fuzzy_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

        # DON'T set the completer on the widget at all
        # DON'T even call setWidget() - we'll position popup manually
        # This is the ONLY way to prevent Qt's auto-insertion

        # Connect text changed signal for comma-separated tag handling
        # Block signals temporarily to prevent recursion
        self.tags_input.textChanged.connect(self._on_tags_input_changed)

        # Handle manual selection from popup (both Enter key and mouse click)
        self.fuzzy_completer.activated.connect(self._on_completion_selected)

        # Replace default popup with custom NoFocusListView to prevent focus stealing
        custom_popup = NoFocusListView()
        custom_popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        # DON'T set focus proxy - it interferes with normal focus behavior

        # CRITICAL FIX: Use Tool window type instead of Popup
        # Popup windows can become the "active window" at OS level (Event 51 = WindowActivate)
        # even with WA_ShowWithoutActivating, which causes keyboard events to route to popup
        # Tool windows are designed to stay in background and never steal activation
        custom_popup.setWindowFlags(
            Qt.WindowType.Tool  # Tool window - never becomes active window
            | Qt.WindowType.FramelessWindowHint  # No title bar
            | Qt.WindowType.WindowStaysOnTopHint  # Always visible above parent
        )
        custom_popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        # Additional attributes to prevent activation
        custom_popup.setAttribute(Qt.WidgetAttribute.WA_X11DoNotAcceptFocus)

        # Set the custom popup on the completer
        self.fuzzy_completer.setPopup(custom_popup)

        # Get reference to our custom popup for later use
        popup = self.fuzzy_completer.popup()

        # Connect popup click to selection handler
        popup.clicked.connect(
            lambda index: self._on_completion_selected(
                self.fuzzy_completer.model().data(index, Qt.ItemDataRole.DisplayRole)
            )
        )

        # Install event filter for keyboard event routing and popup dismissal
        self.focus_protector = InputFocusProtector()
        self.focus_protector.popup = popup
        self.focus_protector.completion_handler = self._on_completion_selected
        self.tags_input.installEventFilter(self.focus_protector)

    def _on_completion_selected(self, completion: str):
        """
        Handle user selecting a tag from the autocomplete popup.

        Args:
            completion: The selected tag
        """
        current_text = self.tags_input.text()

        # Replace the current tag being typed with the selected completion
        if "," in current_text:
            # Multi-tag: replace last tag
            parts = current_text.split(",")
            parts[-1] = " " + completion  # Add space before tag
            new_text = ",".join(parts)
        else:
            # Single tag: replace entire text
            new_text = completion

        # Update the text field (block signals to prevent triggering textChanged)
        self.tags_input.blockSignals(True)
        self.tags_input.setText(new_text)
        self.tags_input.blockSignals(False)

        # Hide the popup after selection
        popup = self.fuzzy_completer.popup()
        popup.hide()

        # Set focus back to input
        self.tags_input.setFocus()

    def _on_tags_input_changed(self, text: str):
        """
        Handle comma-separated tag input.

        Extracts the current tag being typed (after last comma) and
        updates the completer to provide suggestions for that tag only.

        Args:
            text: Current text in tags_input field
        """
        if not hasattr(self, "fuzzy_completer") or not hasattr(self, "all_tags"):
            return

        # Extract current tag being typed (after last comma)
        if "," in text:
            # Split by comma and get the last part (current tag)
            parts = text.split(",")
            current_tag = parts[-1].lstrip()  # Only strip left whitespace
        else:
            # No comma - treat entire text as single tag
            current_tag = text

        # Get fuzzy matches manually
        from rapidfuzz import fuzz
        from PySide6.QtCore import QStringListModel

        if not current_tag.strip():
            # Show first 10 tags when empty
            matches = self.all_tags[:10]
        else:
            # Consecutive character matching (prefix or substring)
            match_lower = current_tag.lower().strip()
            scored_matches = []

            for tag in self.all_tags:
                tag_lower = tag.lower()

                # Priority 1: Exact prefix match (e.g., "py" matches "python")
                if tag_lower.startswith(match_lower):
                    score = 100
                # Priority 2: Contains as consecutive substring (e.g., "side" matches "pyside")
                elif match_lower in tag_lower:
                    score = 80
                # Priority 3: Fuzzy match for typos (e.g., "pyton" matches "python")
                else:
                    fuzzy_score = fuzz.ratio(match_lower, tag_lower)
                    if fuzzy_score >= 70:  # Higher threshold for fuzzy
                        score = fuzzy_score
                    else:
                        continue  # Skip this tag

                scored_matches.append((tag, score))

            # Sort by score (descending), then alphabetically
            scored_matches.sort(key=lambda x: (-x[1], x[0]))
            matches = [tag for tag, score in scored_matches[:10]]

        # Get popup reference and update model
        popup = self.fuzzy_completer.popup()
        model = QStringListModel(matches)
        popup.setModel(model)

        # Show/update/hide the popup
        if matches:
            # Only show popup if it's not already visible
            if not popup.isVisible():
                # Position popup below the tags_input field
                input_pos = self.tags_input.mapToGlobal(
                    self.tags_input.rect().bottomLeft()
                )
                popup_width = max(self.tags_input.width(), 200)
                popup.setFixedWidth(popup_width)
                popup.move(input_pos)

                # Show and raise the popup
                popup.show()
                popup.raise_()

                # Ensure focus stays on tags_input (prevents OS-level window activation)
                from PySide6.QtWidgets import QApplication

                self.tags_input.setFocus(Qt.FocusReason.OtherFocusReason)
                QApplication.processEvents()
        else:
            # No matches - hide popup
            if popup.isVisible():
                popup.hide()

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
            for tag in tags_str.split(","):
                tag = tag.strip()
                if tag:
                    # Normalize: lowercase, replace spaces with dashes
                    normalized_tag = tag.lower().replace(" ", "-")
                    # Remove special characters except hyphens and underscores
                    normalized_tag = "".join(
                        c for c in normalized_tag if c.isalnum() or c in "-_"
                    )
                    if normalized_tag:  # Only add if not empty after normalization
                        tags.append(normalized_tag)
        else:
            tags = []

        # Generate ID from name (lowercase, replace spaces with hyphens)
        snippet_id = name.lower().replace(" ", "-")
        # Remove special characters except hyphens and underscores
        snippet_id = "".join(c for c in snippet_id if c.isalnum() or c in "-_")

        # Get current timestamp
        today = datetime.now().strftime("%Y-%m-%d")

        # Store snippet data
        self.snippet_data = {
            "id": snippet_id,
            "name": name,
            "description": description if description else name,
            "content": content,
            "tags": tags,
            "created": today,
            "modified": today,
        }

        self.accept()

    def get_snippet_data(self):
        """
        Get the snippet data from the dialog.

        Returns:
            Dictionary with snippet fields, or None if cancelled
        """
        return self.snippet_data
