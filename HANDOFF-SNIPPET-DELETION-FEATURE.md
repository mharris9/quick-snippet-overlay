# HANDOFF: Snippet Deletion Feature with Mass Delete and Filtering

**Project:** Quick Snippet Overlay
**Feature:** Easy snippet deletion with mass delete and filtering capabilities
**Priority:** Enhancement - User Experience Improvement
**Date:** 2025-11-06
**Current Status:** Phase 5 Complete + Quick Add Button Enhancement - Ready for deletion feature

---

## 🎯 FEATURE REQUEST

### User Goal
Provide an easy way to delete snippets without manually editing the YAML file. Users should be able to:
1. Access deletion feature in **1 click from the main overlay**
2. See a **list of all snippets with checkboxes**
3. **Select multiple snippets** for mass deletion
4. **Filter snippets** (e.g., by title, tags, content) to find specific ones to delete
5. **Confirm deletion** before actually deleting

### User Quote
> "I need an easy way to delete snippets. I don't want to have to manually edit the yaml file. Create a prompt for a new session to develop this enhancement. Again I want it to be accessible in one click from the main overlay. Ideally I'm provided a list of snippets with checkboxes and I can select all I want to delete and mass delete them. Even nicer would be if there were a filter to pull up a subset of snippets to delete (eg, every snippet with the word 'test' in the title, etc.)."

---

## 📋 CURRENT STATE

### Project Status
- **Phase 5**: Tag Autocomplete - ✅ COMPLETE
- **Enhancement**: Quick Add Button (+ button and Ctrl+N) - ✅ COMPLETE
- **Repository**: https://github.com/mharris9/quick-snippet-overlay
- **Tests**: 129/133 passing (97%)
- **Coverage**: 84%

### Current Snippet Management
**Files:**
- `src/snippet_manager.py` - Handles YAML loading/saving
- `src/snippet_editor_dialog.py` - Add/Edit individual snippets
- `src/overlay_window.py` - Main overlay with search

**Current Capabilities:**
- ✅ Add snippets (via system tray or overlay + button)
- ✅ Edit snippets (via system tray → Edit Snippets)
- ❌ Delete snippets (must manually edit YAML file)

**Current Overlay Features:**
- Search input with fuzzy matching
- Results list showing matching snippets
- `+ New` button (top-right) to add snippets
- Ctrl+N keyboard shortcut for adding
- ESC to close, Enter to copy

---

## 💡 DESIGN CONSIDERATIONS

### Option 1: Delete Button Next to + Button (RECOMMENDED)
Add a "🗑️ Delete" button next to the "+ New" button in the overlay.

**Placement:**
```
┌─────────────────────────────────────────┐
│  [Search input field]     [🗑️] [+]     │ ← Buttons here
├─────────────────────────────────────────┤
│  Snippet 1 name                         │
│  Snippet 2 name                         │
│  Snippet 3 name                         │
│  ...                                    │
└─────────────────────────────────────────┘
```

**Interaction:**
1. Click 🗑️ button
2. Opens "Delete Snippets" dialog
3. Shows list of all snippets with checkboxes
4. Filter bar at top to search
5. Select snippets → Click "Delete Selected"
6. Confirmation dialog → Delete

**Pros:**
- Single click to access
- Consistent with + button placement
- Clear visual indicator

**Cons:**
- Adds another button to UI
- Potential for accidental clicks

### Option 2: Context Menu on Right-Click (Alternative)
Right-click on snippet in results list → "Delete Snippet" option.

**Pros:**
- No extra buttons
- Contextual (delete specific snippet)

**Cons:**
- Requires 2 clicks (right-click + select)
- No mass delete capability
- Less discoverable

### Option 3: Keyboard Shortcut + Button (BEST UX)
Combine Option 1 with keyboard shortcut (e.g., Ctrl+D or Ctrl+Shift+D).

**Pros:**
- Visual button for discoverability
- Keyboard shortcut for power users
- Supports mass delete workflow

**Cons:**
- Need to ensure shortcut doesn't conflict

### Recommended Approach: Option 3
- Add 🗑️ button next to + button
- Implement Ctrl+D keyboard shortcut
- Both open same "Delete Snippets" dialog

---

## 🎨 DELETE SNIPPETS DIALOG - UI DESIGN

### Dialog Layout

```
┌──────────────────────────────────────────────────────┐
│  Delete Snippets                               [X]   │
├──────────────────────────────────────────────────────┤
│  Filter: [________________________] [Clear]          │ ← Filter input
│                                                       │
│  [☐] Select All / Deselect All                       │ ← Checkbox
│                                                       │
│  ┌────────────────────────────────────────────────┐ │
│  │ [☐] Git Clone Command                         │ │
│  │     Tags: git, devops                         │ │
│  │     Created: 2025-11-04                       │ │
│  │                                               │ │ ← Scrollable
│  │ [☐] Python Debug Print                       │ │    list
│  │     Tags: python, debugging                   │ │
│  │     Created: 2025-11-03                       │ │
│  │                                               │ │
│  │ [☑] Test Snippet 1                            │ │ ← Checked
│  │     Tags: test                                │ │
│  │     Created: 2025-11-01                       │ │
│  │                                               │ │
│  │ [☑] Test Snippet 2                            │ │ ← Checked
│  │     Tags: test                                │ │
│  │     Created: 2025-11-01                       │ │
│  └────────────────────────────────────────────────┘ │
│                                                       │
│  2 snippets selected                                 │ ← Selection count
│                                                       │
│  [Delete Selected (2)] [Cancel]                      │ ← Action buttons
└──────────────────────────────────────────────────────┘
```

### Filter Functionality

**Filter Matches:**
- Snippet name (case-insensitive)
- Snippet description
- Snippet tags
- Snippet content

**Filter Behavior:**
- Real-time filtering (debounced 150ms)
- Shows only matching snippets
- Preserves existing checkbox states
- Clear button resets filter

**Example:**
- User types "test" → Shows only snippets with "test" in name/description/tags/content
- User checks all visible snippets
- User clears filter → All snippets shown again, "test" snippets remain checked

### Checkbox Behavior

**Select All/Deselect All:**
- Toggles ALL visible snippets (respects current filter)
- If filter active: "Select All Filtered" / "Deselect All Filtered"
- Updates button text based on state

**Individual Checkboxes:**
- Each snippet has its own checkbox
- Clicking checkbox toggles selection
- Selection count updates in real-time

**Visual Feedback:**
- Selected snippets: Highlighted background
- Hover state: Light highlight
- Checkbox focus indicator for keyboard nav

### Deletion Confirmation

**Confirmation Dialog:**
```
┌────────────────────────────────────────┐
│  Confirm Deletion                      │
├────────────────────────────────────────┤
│  Are you sure you want to delete       │
│  2 snippet(s)?                         │
│                                        │
│  This action cannot be undone.         │
│                                        │
│  Snippets to be deleted:               │
│  • Test Snippet 1                      │
│  • Test Snippet 2                      │
│                                        │
│  [Yes, Delete] [Cancel]                │
└────────────────────────────────────────┘
```

**Confirmation Conditions:**
- Always show confirmation (prevent accidental deletion)
- List snippet names being deleted
- "Yes, Delete" button is red (destructive action)
- ESC key cancels (safe default)

---

## 🔧 TECHNICAL IMPLEMENTATION

### Step 1: Add Delete Button to Overlay

**File:** `src/overlay_window.py`

**Modify `_setup_ui()` to add delete button:**

```python
# Top layout: search input + delete button + add button
top_layout = QHBoxLayout()

# Search input
self.search_input = QLineEdit()
self.search_input.setPlaceholderText("Search snippets...")
self.search_input.setFixedHeight(40)
font = self.search_input.font()
font.setPointSize(16)
self.search_input.setFont(font)
top_layout.addWidget(self.search_input)

# Delete button
self.delete_button = QPushButton("🗑️")  # or "Del"
self.delete_button.setToolTip("Delete Snippets (Ctrl+D)")
self.delete_button.setFixedSize(40, 40)
self.delete_button.clicked.connect(self._on_delete_snippets_clicked)
self.delete_button.setStyleSheet("""
    QPushButton {
        background-color: #d32f2f;  /* Red for destructive action */
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
""")
top_layout.addWidget(self.delete_button)

# Add snippet button (existing)
self.add_button = QPushButton("+")
# ... (existing code)
top_layout.addWidget(self.add_button)

layout.addLayout(top_layout)
```

**Add handler method:**

```python
def _on_delete_snippets_clicked(self):
    """Open the Delete Snippets dialog."""
    from src.delete_snippets_dialog import DeleteSnippetsDialog

    # Get all snippets from snippet_manager
    snippets = self.snippet_manager.get_all_snippets()

    # Create and show dialog
    dialog = DeleteSnippetsDialog(
        snippets=snippets,
        snippet_manager=self.snippet_manager,
        parent=self
    )

    # Show dialog modally
    result = dialog.exec()

    # If snippets were deleted, refresh the overlay results
    if result == QDialog.DialogCode.Accepted:
        # Reload snippets (snippet_manager watches file, but force refresh)
        self._update_results(self.search_input.text())

        # Restore focus to search input
        self.search_input.setFocus()
```

**Add Ctrl+D keyboard shortcut:**

```python
def keyPressEvent(self, event: QKeyEvent):
    """Handle keyboard events (Ctrl+N, Ctrl+D, Enter, ESC, arrows)."""
    # Ctrl+N to add new snippet (existing)
    if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        self._on_add_snippet_clicked()
        event.accept()
        return
    # Ctrl+D to delete snippets (NEW)
    elif event.key() == Qt.Key.Key_D and event.modifiers() == Qt.KeyboardModifier.ControlModifier:
        self._on_delete_snippets_clicked()
        event.accept()
        return
    elif event.key() == Qt.Key.Key_Escape:
        self.hide_overlay()
    # ... (rest of existing code)
```

### Step 2: Create Delete Snippets Dialog

**File:** `src/delete_snippets_dialog.py` (NEW FILE)

**Class Structure:**

```python
"""
Delete Snippets Dialog - Mass snippet deletion with filtering

This module provides a dialog for selecting and deleting multiple snippets
with filtering capabilities.

Classes:
    SnippetCheckboxItem: QWidget for snippet with checkbox
    DeleteSnippetsDialog: Main deletion dialog
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton,
    QScrollArea, QWidget, QCheckBox, QLabel, QMessageBox
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
        self.filter_input.setPlaceholderText("Filter snippets by name, tags, or content...")
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
        self.delete_button.setStyleSheet("""
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
        """)
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
        checked = (state == Qt.CheckState.Checked.value)

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
            QMessageBox.StandardButton.No  # Default to No (safe)
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
                self,
                "Success",
                f"Successfully deleted {len(snippets)} snippet(s)."
            )
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to delete snippets: {str(e)}"
            )
```

### Step 3: Add Delete Method to SnippetManager

**File:** `src/snippet_manager.py`

**Add new method:**

```python
def delete_snippets(self, snippet_ids: List[str]) -> None:
    """
    Delete multiple snippets by their IDs.

    Args:
        snippet_ids: List of snippet IDs to delete

    Raises:
        ValueError: If any snippet ID is not found
        IOError: If YAML file cannot be written
    """
    # Load current snippets
    current_snippets = self.load()

    # Verify all IDs exist
    existing_ids = {s.id for s in current_snippets}
    for snippet_id in snippet_ids:
        if snippet_id not in existing_ids:
            raise ValueError(f"Snippet with ID '{snippet_id}' not found")

    # Filter out snippets to delete
    remaining_snippets = [s for s in current_snippets if s.id not in snippet_ids]

    # Save updated snippets
    self._save_snippets(remaining_snippets)

    logging.info(f"Deleted {len(snippet_ids)} snippet(s): {snippet_ids}")

def _save_snippets(self, snippets: List[Snippet]) -> None:
    """
    Save snippets to YAML file.

    Args:
        snippets: List of Snippet objects to save

    Raises:
        IOError: If file cannot be written
    """
    # Convert snippets to dict format
    snippets_data = {
        "version": 1,
        "snippets": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "content": s.content,
                "tags": s.tags,
                "created": s.created,
                "modified": s.modified
            }
            for s in snippets
        ]
    }

    # Write to file
    try:
        with open(self.file_path, 'w', encoding='utf-8') as f:
            yaml.dump(snippets_data, f, default_flow_style=False, allow_unicode=True)

        logging.info(f"Saved {len(snippets)} snippets to {self.file_path}")
    except Exception as e:
        logging.error(f"Failed to save snippets: {e}")
        raise IOError(f"Failed to save snippets: {e}")

def get_all_snippets(self) -> List[Snippet]:
    """
    Get all snippets (convenience method).

    Returns:
        List of all Snippet objects
    """
    return self.load()
```

---

## 🧪 TESTING REQUIREMENTS

### Manual Testing

**Test Case 1: Delete Button Exists**
1. Press `Ctrl+Shift+Space` to open overlay
2. **Expected:** 🗑️ button visible next to + button
3. **Expected:** Tooltip shows "Delete Snippets (Ctrl+D)"

**Test Case 2: Open Delete Dialog via Button**
1. Open overlay
2. Click 🗑️ button
3. **Expected:** Delete Snippets dialog opens
4. **Expected:** All snippets listed with checkboxes
5. **Expected:** Filter input at top
6. **Expected:** Select All checkbox visible

**Test Case 3: Open Delete Dialog via Ctrl+D**
1. Open overlay
2. Press `Ctrl+D`
3. **Expected:** Delete Snippets dialog opens

**Test Case 4: Filter Snippets**
1. Open delete dialog
2. Type "test" in filter input
3. **Expected:** Only snippets with "test" in name/tags/content shown
4. Type "python"
5. **Expected:** Only snippets with "python" shown
6. Click "Clear" button
7. **Expected:** All snippets shown again

**Test Case 5: Select All**
1. Open delete dialog
2. Check "Select All" checkbox
3. **Expected:** All visible snippets checked
4. **Expected:** Selection count updates (e.g., "10 snippets selected")
5. Uncheck "Select All"
6. **Expected:** All visible snippets unchecked
7. **Expected:** Selection count shows "0 snippets selected"

**Test Case 6: Select All with Filter**
1. Open delete dialog
2. Type "test" in filter (shows 3 snippets)
3. Check "Select All"
4. **Expected:** Only the 3 visible snippets checked
5. Clear filter
6. **Expected:** Only those 3 snippets remain checked, others unchecked

**Test Case 7: Delete Single Snippet**
1. Open delete dialog
2. Check 1 snippet
3. Click "Delete Selected (1)"
4. **Expected:** Confirmation dialog appears with snippet name
5. Click "Yes, Delete"
6. **Expected:** Success message
7. **Expected:** Dialog closes
8. **Expected:** Overlay refreshes, snippet gone

**Test Case 8: Mass Delete**
1. Open delete dialog
2. Check multiple snippets (e.g., 5)
3. **Expected:** Button shows "Delete Selected (5)"
4. Click delete button
5. **Expected:** Confirmation lists all 5 snippet names
6. Click "Yes, Delete"
7. **Expected:** All 5 snippets deleted
8. **Expected:** Overlay refreshes

**Test Case 9: Cancel Deletion**
1. Open delete dialog
2. Check snippets
3. Click "Delete Selected"
4. Click "No" in confirmation
5. **Expected:** Dialog stays open, nothing deleted
6. Click "Cancel" button
7. **Expected:** Dialog closes, nothing deleted

**Test Case 10: Delete Button Disabled When None Selected**
1. Open delete dialog
2. **Expected:** "Delete Selected (0)" button is disabled (grayed out)
3. Check 1 snippet
4. **Expected:** Button enabled
5. Uncheck snippet
6. **Expected:** Button disabled again

**Test Case 11: Real-time Selection Count**
1. Open delete dialog
2. Check snippet 1
3. **Expected:** "1 snippet(s) selected"
4. Check snippet 2
5. **Expected:** "2 snippet(s) selected"
6. Uncheck snippet 1
7. **Expected:** "1 snippet(s) selected"

### Automated Testing

**File:** `tests/test_delete_snippets_dialog.py` (NEW FILE)

```python
"""
Tests for delete_snippets_dialog.py - Snippet deletion with filtering
"""

import pytest
from unittest.mock import Mock, patch
from PySide6.QtWidgets import QDialog
from src.delete_snippets_dialog import DeleteSnippetsDialog, SnippetCheckboxItem
from src.snippet_manager import Snippet


@pytest.fixture
def sample_snippets():
    """Create sample snippets for testing."""
    return [
        Snippet(
            id="test-1",
            name="Test Snippet 1",
            description="Test description",
            content="echo test",
            tags=["test"],
            created="2025-11-01",
            modified="2025-11-01"
        ),
        Snippet(
            id="python-1",
            name="Python Debug",
            description="Python debugging",
            content="print('debug')",
            tags=["python", "debugging"],
            created="2025-11-02",
            modified="2025-11-02"
        ),
        Snippet(
            id="git-1",
            name="Git Clone",
            description="Git clone command",
            content="git clone",
            tags=["git", "devops"],
            created="2025-11-03",
            modified="2025-11-03"
        )
    ]


def test_snippet_checkbox_item_creation(sample_snippets, qtbot):
    """Test SnippetCheckboxItem creates correctly."""
    snippet = sample_snippets[0]
    item = SnippetCheckboxItem(snippet)
    qtbot.addWidget(item)

    assert item.snippet == snippet
    assert not item.is_checked()


def test_snippet_checkbox_item_matches_filter(sample_snippets):
    """Test filter matching logic."""
    item = SnippetCheckboxItem(sample_snippets[0])

    assert item.matches_filter("test")
    assert item.matches_filter("Test")  # Case insensitive
    assert item.matches_filter("snippet")
    assert not item.matches_filter("python")


def test_delete_dialog_creation(sample_snippets, qtbot):
    """Test dialog initializes correctly."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    assert dialog.windowTitle() == "Delete Snippets"
    assert len(dialog.snippet_items) == 3


def test_delete_dialog_filter(sample_snippets, qtbot):
    """Test filtering functionality."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    # Apply filter
    dialog.filter_input.setText("python")
    dialog._apply_filter("python")

    # Count visible items
    visible_count = sum(1 for item in dialog.snippet_items if item.isVisible())
    assert visible_count == 1


def test_select_all_checkbox(sample_snippets, qtbot):
    """Test select all functionality."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    # Check select all
    dialog.select_all_checkbox.setChecked(True)
    dialog._on_select_all_changed(2)  # Qt.CheckState.Checked

    # Verify all checked
    assert all(item.is_checked() for item in dialog.snippet_items)


def test_delete_button_state(sample_snippets, qtbot):
    """Test delete button enabled/disabled based on selection."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    # Initially disabled
    assert not dialog.delete_button.isEnabled()

    # Check one item
    dialog.snippet_items[0].set_checked(True)
    dialog._update_selection_count()

    # Now enabled
    assert dialog.delete_button.isEnabled()
    assert "Delete Selected (1)" in dialog.delete_button.text()


def test_delete_confirmation_shown(sample_snippets, qtbot):
    """Test confirmation dialog appears."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch('src.delete_snippets_dialog.QMessageBox.question') as mock_msg:
        mock_msg.return_value = QMessageBox.StandardButton.No

        dialog._on_delete_clicked()

        # Verify confirmation shown
        mock_msg.assert_called_once()


def test_delete_snippets_called(sample_snippets, qtbot):
    """Test snippet_manager.delete_snippets is called."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)
    qtbot.addWidget(dialog)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch('src.delete_snippets_dialog.QMessageBox.question') as mock_msg:
        mock_msg.return_value = QMessageBox.StandardButton.Yes

        with patch('src.delete_snippets_dialog.QMessageBox.information'):
            dialog._on_delete_clicked()

    # Verify delete_snippets called with correct ID
    mock_manager.delete_snippets.assert_called_once_with(['test-1'])
```

**File:** `tests/test_snippet_manager.py` (ADD TESTS)

```python
def test_delete_snippets(temp_snippets_file):
    """Test deleting multiple snippets."""
    manager = SnippetManager(str(temp_snippets_file))

    # Load initial snippets
    initial_snippets = manager.load()
    initial_count = len(initial_snippets)

    # Delete 2 snippets
    ids_to_delete = [initial_snippets[0].id, initial_snippets[1].id]
    manager.delete_snippets(ids_to_delete)

    # Reload and verify
    remaining_snippets = manager.load()
    assert len(remaining_snippets) == initial_count - 2
    assert all(s.id not in ids_to_delete for s in remaining_snippets)


def test_delete_nonexistent_snippet(temp_snippets_file):
    """Test deleting non-existent snippet raises error."""
    manager = SnippetManager(str(temp_snippets_file))

    with pytest.raises(ValueError, match="not found"):
        manager.delete_snippets(['nonexistent-id'])


def test_get_all_snippets(temp_snippets_file):
    """Test get_all_snippets convenience method."""
    manager = SnippetManager(str(temp_snippets_file))

    snippets = manager.get_all_snippets()
    assert isinstance(snippets, list)
    assert len(snippets) > 0
```

**File:** `tests/test_overlay_window.py` (ADD TESTS)

```python
def test_delete_button_exists(overlay_window):
    """Test that delete button is present in overlay."""
    assert hasattr(overlay_window, 'delete_button')
    assert overlay_window.delete_button is not None
    assert overlay_window.delete_button.toolTip() == "Delete Snippets (Ctrl+D)"


def test_delete_button_click_opens_dialog(overlay_window):
    """Test clicking delete button opens DeleteSnippetsDialog."""
    with patch('src.delete_snippets_dialog.DeleteSnippetsDialog') as mock_dialog_class:
        mock_dialog = Mock()
        mock_dialog.exec.return_value = 0
        mock_dialog_class.return_value = mock_dialog

        overlay_window.delete_button.click()

        mock_dialog_class.assert_called_once()
        mock_dialog.exec.assert_called_once()


def test_ctrl_d_shortcut_opens_delete_dialog(overlay_window):
    """Test Ctrl+D keyboard shortcut opens delete dialog."""
    from PySide6.QtGui import QKeyEvent
    from PySide6.QtCore import QEvent

    with patch('src.delete_snippets_dialog.DeleteSnippetsDialog') as mock_dialog_class:
        mock_dialog = Mock()
        mock_dialog.exec.return_value = 0
        mock_dialog_class.return_value = mock_dialog

        key_event = QKeyEvent(
            QEvent.Type.KeyPress,
            Qt.Key.Key_D,
            Qt.KeyboardModifier.ControlModifier
        )

        overlay_window.keyPressEvent(key_event)

        mock_dialog_class.assert_called_once()
        mock_dialog.exec.assert_called_once()
```

---

## 📁 FILES TO MODIFY/CREATE

### Create New Files
1. **src/delete_snippets_dialog.py** (NEW)
   - `SnippetCheckboxItem` class
   - `DeleteSnippetsDialog` class
   - Full implementation with filtering

2. **tests/test_delete_snippets_dialog.py** (NEW)
   - Tests for dialog functionality
   - Tests for filtering
   - Tests for selection logic
   - Tests for deletion confirmation

### Modify Existing Files
3. **src/overlay_window.py**
   - Add delete button to UI
   - Add `_on_delete_snippets_clicked()` handler
   - Add Ctrl+D keyboard shortcut
   - Update docstrings

4. **src/snippet_manager.py**
   - Add `delete_snippets(snippet_ids: List[str])` method
   - Add `_save_snippets(snippets: List[Snippet])` helper
   - Add `get_all_snippets()` convenience method

5. **tests/test_snippet_manager.py**
   - Add `test_delete_snippets()`
   - Add `test_delete_nonexistent_snippet()`
   - Add `test_get_all_snippets()`

6. **tests/test_overlay_window.py**
   - Add `test_delete_button_exists()`
   - Add `test_delete_button_click_opens_dialog()`
   - Add `test_ctrl_d_shortcut_opens_delete_dialog()`

7. **CLAUDE.md**
   - Update overlay features to mention delete button
   - Document Ctrl+D keyboard shortcut

---

## ⚠️ POTENTIAL ISSUES & SOLUTIONS

### Issue 1: Accidental Deletion
**Problem:** Users might accidentally click delete button.

**Solution:**
- Always show confirmation dialog before deletion
- Default to "No" in confirmation
- Make delete button red (signals danger)
- List snippet names in confirmation
- ESC key cancels confirmation

### Issue 2: Performance with Large Libraries
**Problem:** Showing 1000+ snippets in dialog might be slow.

**Solution:**
- Use QScrollArea for efficient rendering
- Only render visible items (Qt handles this)
- Debounce filter input (150ms)
- Consider pagination if > 500 snippets (future enhancement)

### Issue 3: Filter State Management
**Problem:** Selecting filtered items, then clearing filter might confuse users.

**Solution:**
- Preserve checkbox states when filter changes
- Show selection count even with filter
- Update "Select All" text to "Select All Filtered" when filter active

### Issue 4: Undo Deletion
**Problem:** Users might regret deleting snippets.

**Solution:**
- Strong confirmation dialog (current approach)
- Future enhancement: Create backup before deletion
- Future enhancement: Undo/trash system (Phase 7+)

### Issue 5: Dialog Size on Small Screens
**Problem:** Dialog might be too large for small screens.

**Solution:**
- Set minimum size (600x500)
- Use scrollable areas
- Dialog is resizable by user

### Issue 6: Keyboard Navigation
**Problem:** Users might want to navigate with keyboard only.

**Solution:**
- Tab key navigates between checkboxes
- Space bar toggles checkbox
- Enter key triggers delete (when button focused)
- ESC key closes dialog

---

## 🎯 SUCCESS CRITERIA

### Must Have
- ✅ 🗑️ Delete button visible in overlay
- ✅ Single click opens Delete Snippets dialog
- ✅ Ctrl+D keyboard shortcut works
- ✅ All snippets listed with checkboxes
- ✅ Filter input filters snippets in real-time
- ✅ Select All checkbox works
- ✅ Delete button shows selection count
- ✅ Confirmation dialog before deletion
- ✅ Snippets deleted from YAML file
- ✅ Overlay refreshes after deletion

### Nice to Have
- ✅ Filter respects name, description, tags, and content
- ✅ Clear filter button
- ✅ Real-time selection count
- ✅ Button disabled when nothing selected
- ✅ Visual feedback (hover states, colors)
- ✅ Dark theme consistency
- ✅ Snippet metadata shown (tags, date)

### Polish
- ✅ Red color scheme for destructive action
- ✅ Confirmation lists snippet names
- ✅ Success message after deletion
- ✅ Error handling with user-friendly messages
- ✅ Keyboard navigation support
- ✅ Accessible (screen readers, keyboard-only)

---

## 📊 ESTIMATED EFFORT

**Time:** 3-4 hours
**Complexity:** Medium
**Risk:** Medium (modifies data file, needs careful testing)

**Breakdown:**
- Create `delete_snippets_dialog.py`: 90 min
- Add `delete_snippets()` to `snippet_manager.py`: 30 min
- Add delete button to overlay: 20 min
- Add Ctrl+D shortcut: 10 min
- Write automated tests: 60 min
- Manual testing: 30 min
- Documentation: 20 min

---

## 🔮 FUTURE ENHANCEMENTS

### Phase 1 (This Session)
- Basic deletion with filtering
- Mass delete capability
- Confirmation dialog

### Phase 2 (Future)
- Undo deletion (trash/recycle bin)
- Bulk export before deletion
- Deletion history/audit log

### Phase 3 (Future)
- Advanced filters (date range, tag combinations)
- Smart suggestions ("Delete all test snippets?")
- Keyboard shortcuts for rapid deletion

---

## 📝 IMPLEMENTATION CHECKLIST

Before starting:
- [ ] Read this document fully
- [ ] Understand current snippet_manager API
- [ ] Review existing dialog patterns (snippet_editor_dialog.py)
- [ ] Check test fixtures and patterns

During implementation:
- [ ] Create `delete_snippets_dialog.py` with full functionality
- [ ] Add `delete_snippets()` to snippet_manager
- [ ] Add delete button to overlay UI
- [ ] Implement Ctrl+D shortcut
- [ ] Write comprehensive tests
- [ ] Test manually with various scenarios
- [ ] Verify YAML file updates correctly
- [ ] Test edge cases (empty list, single item, all items)

After implementation:
- [ ] Run full test suite (`pytest`)
- [ ] Verify no regressions in existing features
- [ ] Format code (`black src/ tests/`)
- [ ] Update CLAUDE.md documentation
- [ ] Manual testing with actual snippets file
- [ ] Create commit with clear message

---

## 🚀 QUICKSTART

**To implement this feature:**

1. **Create delete dialog file:**
   ```
   src/delete_snippets_dialog.py
   ```
   Use the implementation provided in "Technical Implementation" section.

2. **Modify snippet_manager.py:**
   Add `delete_snippets()`, `_save_snippets()`, and `get_all_snippets()` methods.

3. **Modify overlay_window.py:**
   - Add delete button in `_setup_ui()`
   - Add `_on_delete_snippets_clicked()` handler
   - Add Ctrl+D in `keyPressEvent()`

4. **Create test file:**
   ```
   tests/test_delete_snippets_dialog.py
   ```
   Write tests for all dialog functionality.

5. **Test manually:**
   - Run app: `RUN-APP.bat`
   - Open overlay: Ctrl+Shift+Space
   - Click 🗑️ button
   - Test filtering, selection, deletion

6. **Run automated tests:**
   ```powershell
   pytest tests/test_delete_snippets_dialog.py -v
   pytest tests/test_snippet_manager.py -v
   pytest tests/test_overlay_window.py -v
   ```

7. **Format and commit:**
   ```powershell
   black src/ tests/
   git add .
   git commit -m "Add snippet deletion feature with filtering and mass delete"
   ```

---

## 🔑 KEY DESIGN DECISIONS

### Why Separate Dialog?
- Keeps overlay simple and focused
- Provides dedicated space for filtering
- Allows users to review before deleting
- Easier to test in isolation

### Why Confirmation Dialog?
- Deletion is destructive and irreversible
- Prevents accidental mass deletion
- Best practice for destructive actions
- Gives users chance to review

### Why Filter Instead of Search?
- Filtering is more intuitive for deletion workflow
- Shows all matching items simultaneously
- Allows mass selection of filtered subset
- Clear visual feedback

### Why Checkboxes Instead of Selection?
- Explicit opt-in for deletion
- Supports mass selection easily
- Clear visual indication of what will be deleted
- Familiar pattern from file managers

---

**Generated:** 2025-11-06
**For:** Phase 6 - Snippet Management Enhancement
**Status:** READY TO IMPLEMENT
**Difficulty:** Medium 🟡
**Impact:** High (critical workflow improvement)
**Risk:** Medium (modifies data file - needs careful testing)

---

## 💡 TIPS FOR IMPLEMENTER

1. **Start with snippet_manager.py:** Get the data layer working first with tests.

2. **Create minimal dialog first:** Start with basic list and checkboxes, add filtering later.

3. **Test incrementally:** Test each feature as you add it (filtering, selection, deletion).

4. **Use existing patterns:** Reference `snippet_editor_dialog.py` for dialog structure and styling.

5. **Handle errors gracefully:** Wrap file operations in try/except and show user-friendly messages.

6. **Visual feedback is key:** Users need to see selection count, filter results, disabled states.

7. **Test with real data:** Create test snippets file with 20+ snippets to verify performance.

8. **Keyboard shortcuts matter:** Ensure Tab, Space, Enter, ESC all work intuitively.

9. **Dark theme consistency:** Match existing overlay/dialog styling exactly.

10. **Confirmation is critical:** Never delete without explicit user confirmation.

Good luck! This feature will significantly improve the user experience. 🚀
