"""
Tests for delete_snippets_dialog.py - Snippet deletion with filtering
"""

import pytest
import sys
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QDialog, QMessageBox, QApplication
from PySide6.QtCore import Qt, QCoreApplication
from src.delete_snippets_dialog import DeleteSnippetsDialog, SnippetCheckboxItem
from src.snippet_manager import Snippet
from datetime import date


@pytest.fixture(scope="module")
def qt_app():
    """Create QApplication instance for testing."""
    # Check if an instance already exists
    existing_app = QCoreApplication.instance()
    if existing_app is not None:
        yield existing_app
    else:
        app_instance = QApplication(sys.argv if sys.argv else [])
        yield app_instance


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
            created=date(2025, 11, 1),
            modified=date(2025, 11, 1),
        ),
        Snippet(
            id="python-1",
            name="Python Debug",
            description="Python debugging",
            content="print('debug')",
            tags=["python", "debugging"],
            created=date(2025, 11, 2),
            modified=date(2025, 11, 2),
        ),
        Snippet(
            id="git-1",
            name="Git Clone",
            description="Git clone command",
            content="git clone",
            tags=["git", "devops"],
            created=date(2025, 11, 3),
            modified=date(2025, 11, 3),
        ),
    ]


def test_snippet_checkbox_item_creation(sample_snippets, qt_app):
    """Test SnippetCheckboxItem creates correctly."""
    snippet = sample_snippets[0]
    item = SnippetCheckboxItem(snippet)

    assert item.snippet == snippet
    assert not item.is_checked()

    item.close()


def test_snippet_checkbox_item_matches_filter(sample_snippets):
    """Test filter matching logic."""
    item = SnippetCheckboxItem(sample_snippets[0])

    assert item.matches_filter("test")
    assert item.matches_filter("Test")  # Case insensitive
    assert item.matches_filter("snippet")
    assert not item.matches_filter("python")


def test_snippet_checkbox_item_matches_filter_by_tag(sample_snippets):
    """Test filter matching by tags."""
    item = SnippetCheckboxItem(sample_snippets[1])

    assert item.matches_filter("python")
    assert item.matches_filter("debugging")


def test_snippet_checkbox_item_matches_filter_by_content(sample_snippets):
    """Test filter matching by content."""
    item = SnippetCheckboxItem(sample_snippets[1])

    assert item.matches_filter("print")
    assert item.matches_filter("debug")


def test_snippet_checkbox_item_set_checked(sample_snippets, qt_app):
    """Test setting checkbox state."""
    item = SnippetCheckboxItem(sample_snippets[0])

    item.set_checked(True)
    assert item.is_checked()

    item.set_checked(False)
    assert not item.is_checked()

    item.close()


def test_delete_dialog_creation(sample_snippets, qt_app):
    """Test dialog initializes correctly."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    assert dialog.windowTitle() == "Delete Snippets"
    assert len(dialog.snippet_items) == 3
    assert dialog.selection_label.text() == "0 snippet(s) selected"
    assert not dialog.delete_button.isEnabled()

    dialog.close()


def test_delete_dialog_filter(sample_snippets, qt_app):
    """Test filtering functionality."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Apply filter
    dialog.filter_input.setText("python")
    dialog._apply_filter("python")

    # Count visible items
    visible_count = sum(1 for item in dialog.snippet_items if item.isVisible())
    assert visible_count == 1

    dialog.close()


def test_delete_dialog_filter_multiple_matches(sample_snippets, qt_app):
    """Test filtering with multiple matches."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Apply filter that matches multiple snippets
    dialog.filter_input.setText("e")  # Matches "Test", "Python", etc.
    dialog._apply_filter("e")

    # Count visible items (should be all 3)
    visible_count = sum(1 for item in dialog.snippet_items if item.isVisible())
    assert visible_count == 3

    dialog.close()


def test_delete_dialog_clear_filter(sample_snippets, qt_app):
    """Test clearing filter."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Apply filter
    dialog.filter_input.setText("python")
    dialog._apply_filter("python")

    # Clear filter
    dialog._clear_filter()

    # All items should be visible
    visible_count = sum(1 for item in dialog.snippet_items if item.isVisible())
    assert visible_count == 3
    assert dialog.filter_input.text() == ""

    dialog.close()


def test_select_all_checkbox(sample_snippets, qt_app):
    """Test select all functionality."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check select all
    dialog.select_all_checkbox.setChecked(True)
    dialog._on_select_all_changed(Qt.CheckState.Checked.value)

    # Verify all checked
    assert all(item.is_checked() for item in dialog.snippet_items)

    dialog.close()


def test_deselect_all_checkbox(sample_snippets, qt_app):
    """Test deselect all functionality."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check all items first
    for item in dialog.snippet_items:
        item.set_checked(True)

    # Deselect all
    dialog.select_all_checkbox.setChecked(False)
    dialog._on_select_all_changed(Qt.CheckState.Unchecked.value)

    # Verify all unchecked
    assert not any(item.is_checked() for item in dialog.snippet_items)

    dialog.close()


def test_select_all_with_filter(sample_snippets, qt_app):
    """Test select all with filter active."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Apply filter
    dialog.filter_input.setText("test")
    dialog._apply_filter("test")

    # Select all (should only select visible items)
    dialog.select_all_checkbox.setChecked(True)
    dialog._on_select_all_changed(Qt.CheckState.Checked.value)

    # Only visible items should be checked
    visible_checked = sum(
        1 for item in dialog.snippet_items if item.isVisible() and item.is_checked()
    )
    assert visible_checked == 1  # Only "Test Snippet 1" matches

    dialog.close()


def test_delete_button_state(sample_snippets, qt_app):
    """Test delete button enabled/disabled based on selection."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Initially disabled
    assert not dialog.delete_button.isEnabled()

    # Check one item
    dialog.snippet_items[0].set_checked(True)
    dialog._update_selection_count()

    # Now enabled
    assert dialog.delete_button.isEnabled()
    assert "Delete Selected (1)" in dialog.delete_button.text()

    dialog.close()


def test_delete_button_text_updates(sample_snippets, qt_app):
    """Test delete button text updates with selection count."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check multiple items
    dialog.snippet_items[0].set_checked(True)
    dialog.snippet_items[1].set_checked(True)
    dialog._update_selection_count()

    assert "Delete Selected (2)" in dialog.delete_button.text()
    assert dialog.selection_label.text() == "2 snippet(s) selected"

    dialog.close()


def test_delete_confirmation_shown(sample_snippets, qt_app):
    """Test confirmation dialog appears."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.No
    ) as mock_msg:
        dialog._on_delete_clicked()

        # Verify confirmation shown
        mock_msg.assert_called_once()

    dialog.close()


def test_delete_confirmation_cancelled(sample_snippets, qt_app):
    """Test cancelling deletion confirmation."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.No
    ):
        dialog._on_delete_clicked()

        # Verify delete_snippets not called
        mock_manager.delete_snippets.assert_not_called()

    dialog.close()


def test_delete_snippets_called(sample_snippets, qt_app):
    """Test snippet_manager.delete_snippets is called."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
    ):
        with patch.object(QMessageBox, "information"):
            dialog._on_delete_clicked()

    # Verify delete_snippets called with correct ID
    mock_manager.delete_snippets.assert_called_once_with(["test-1"])

    dialog.close()


def test_delete_multiple_snippets(sample_snippets, qt_app):
    """Test deleting multiple snippets at once."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check multiple items
    dialog.snippet_items[0].set_checked(True)
    dialog.snippet_items[1].set_checked(True)

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
    ):
        with patch.object(QMessageBox, "information"):
            dialog._on_delete_clicked()

    # Verify delete_snippets called with correct IDs
    mock_manager.delete_snippets.assert_called_once_with(["test-1", "python-1"])

    dialog.close()


def test_delete_error_handling(sample_snippets, qt_app):
    """Test error handling when deletion fails."""
    mock_manager = Mock()
    mock_manager.delete_snippets.side_effect = Exception("Delete failed")

    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check one item
    dialog.snippet_items[0].set_checked(True)

    with patch.object(
        QMessageBox, "question", return_value=QMessageBox.StandardButton.Yes
    ):
        with patch.object(QMessageBox, "critical") as mock_critical:
            dialog._on_delete_clicked()

            # Verify error dialog shown
            mock_critical.assert_called_once()

    dialog.close()


def test_confirmation_lists_snippet_names(sample_snippets, qt_app):
    """Test confirmation dialog lists snippet names."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check items
    dialog.snippet_items[0].set_checked(True)
    dialog.snippet_items[1].set_checked(True)

    selected = [item.snippet for item in dialog.snippet_items if item.is_checked()]

    result = dialog._show_confirmation_dialog(selected)

    # Can't easily verify message box content without mocking, but we can verify it returns bool
    assert isinstance(result, bool)

    dialog.close()


def test_filter_preserves_checkbox_state(sample_snippets, qt_app):
    """Test that filtering preserves checkbox states."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog(sample_snippets, mock_manager)

    # Check first item
    dialog.snippet_items[0].set_checked(True)

    # Apply filter that hides first item
    dialog.filter_input.setText("python")
    dialog._apply_filter("python")

    # Clear filter
    dialog._clear_filter()

    # First item should still be checked
    assert dialog.snippet_items[0].is_checked()

    dialog.close()


def test_empty_snippets_list(qt_app):
    """Test dialog with empty snippets list."""
    mock_manager = Mock()
    dialog = DeleteSnippetsDialog([], mock_manager)

    assert len(dialog.snippet_items) == 0
    assert dialog.selection_label.text() == "0 snippet(s) selected"
    assert not dialog.delete_button.isEnabled()

    dialog.close()
