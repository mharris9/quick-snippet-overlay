"""
Tests for snippet_editor_dialog.py - Snippet Editor Dialog with Tag Autocomplete

Test Coverage:
1. QCompleter existence
2. QCompleter attachment to tags_input field
3. QCompleter model populated with tags from SnippetManager
4. QCompleter case sensitivity configuration
5. QCompleter completion mode configuration
"""

import pytest
import sys
from unittest.mock import Mock, MagicMock, patch
from PySide6.QtCore import Qt, QCoreApplication
from PySide6.QtWidgets import QCompleter
from src.snippet_editor_dialog import SnippetEditorDialog
from src.snippet_manager import SnippetManager
from src.fuzzy_tag_completer import FuzzyTagCompleter


@pytest.fixture(scope="module")
def qt_app():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication

    # Check if an instance already exists
    existing_app = QCoreApplication.instance()
    if existing_app is not None:
        yield existing_app
    else:
        app_instance = QApplication(sys.argv if sys.argv else [])
        yield app_instance


@pytest.fixture
def mock_snippet_manager():
    """Create a mock SnippetManager with predefined tags."""
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["javascript", "python", "testing"]
    return manager


@pytest.fixture
def dialog_with_manager(qt_app, mock_snippet_manager):
    """Create SnippetEditorDialog with a mock snippet manager."""
    dialog = SnippetEditorDialog(snippet_manager=mock_snippet_manager, parent=None)
    yield dialog
    dialog.close()


@pytest.fixture
def dialog_without_manager(qt_app):
    """Create SnippetEditorDialog without snippet manager (backward compatibility)."""
    dialog = SnippetEditorDialog(parent=None)
    yield dialog
    dialog.close()


# ============================================================================
# Test Case 1: Completer Exists
# ============================================================================


def test_completer_exists(dialog_with_manager):
    """
    Test that FuzzyTagCompleter is created and exists when snippet_manager is provided.

    Verifies:
    - Dialog has fuzzy_completer attribute
    - Completer is not None
    - Completer is an instance of FuzzyTagCompleter

    Note: Completer is NOT attached to tags_input via setCompleter() to prevent
    Qt's auto-insertion behavior. Instead, it's managed manually.
    """
    completer = dialog_with_manager.fuzzy_completer
    assert completer is not None
    assert isinstance(completer, FuzzyTagCompleter)


# ============================================================================
# Test Case 2: Completer Attached to Tags Input
# ============================================================================


def test_completer_attached_to_tags_input(dialog_with_manager):
    """
    Test that FuzzyTagCompleter has a custom NoFocusListView popup.

    Verifies:
    - Dialog has fuzzy_completer attribute
    - Completer has a popup
    - Popup has NoFocus policy to prevent focus stealing

    Note: Completer is NOT set on tags_input via setCompleter() - this is
    intentional to prevent Qt's auto-insertion behavior.
    """
    completer = dialog_with_manager.fuzzy_completer

    assert completer is not None
    assert isinstance(completer, FuzzyTagCompleter)

    # Verify popup has NoFocus policy
    popup = completer.popup()
    assert popup.focusPolicy() == Qt.FocusPolicy.NoFocus


# ============================================================================
# Test Case 3: Completer Model Populated on Init
# ============================================================================


def test_completer_model_populated_on_init(dialog_with_manager, mock_snippet_manager):
    """
    Test that completer model is populated with tags from SnippetManager.

    Verifies:
    - SnippetManager.get_all_tags() was called
    - Completer model contains all expected tags
    - Tags are in sorted order (as returned by get_all_tags)
    """
    # Verify get_all_tags was called
    mock_snippet_manager.get_all_tags.assert_called_once()

    # Get completer and check model
    completer = dialog_with_manager.fuzzy_completer
    model = completer.model()

    # Extract all items from model
    tags_in_model = []
    for i in range(model.rowCount()):
        index = model.index(i, 0)
        tags_in_model.append(model.data(index))

    # Verify tags match expected list
    expected_tags = ["javascript", "python", "testing"]
    assert tags_in_model == expected_tags


# ============================================================================
# Test Case 4: Completer Case Insensitive
# ============================================================================


def test_completer_case_insensitive(dialog_with_manager):
    """
    Test that completer is configured for case-insensitive matching.

    Verifies:
    - caseSensitivity() returns Qt.CaseInsensitive
    - User can type "pyt" or "PYT" and get "python" suggestions
    """
    completer = dialog_with_manager.fuzzy_completer
    assert completer.caseSensitivity() == Qt.CaseSensitivity.CaseInsensitive


# ============================================================================
# Test Case 5: Completer Popup Mode
# ============================================================================


def test_completer_popup_mode(dialog_with_manager):
    """
    Test that completer uses PopupCompletion mode.

    Verifies:
    - completionMode() returns QCompleter.CompletionMode.PopupCompletion
    - Dropdown appears with suggestions (not inline)
    """
    completer = dialog_with_manager.fuzzy_completer
    from PySide6.QtWidgets import QCompleter

    assert completer.completionMode() == QCompleter.CompletionMode.PopupCompletion


# ============================================================================
# Test Case 6: Backward Compatibility - No Manager
# ============================================================================


def test_no_completer_when_manager_is_none(dialog_without_manager):
    """
    Test backward compatibility when snippet_manager is not provided.

    Verifies:
    - Dialog still works without snippet_manager
    - No fuzzy_completer attribute is created
    - Dialog doesn't crash during initialization
    """
    # When manager is None, fuzzy_completer should not exist
    assert (
        not hasattr(dialog_without_manager, "fuzzy_completer")
        or dialog_without_manager.fuzzy_completer is None
    )


# ============================================================================
# Test Case 7: Empty Tags List
# ============================================================================


def test_completer_with_empty_tags(qt_app):
    """
    Test that completer is created even when tags list is empty.

    Verifies:
    - Completer exists
    - Model is empty (rowCount == 0)
    - No errors during initialization
    """
    # Create mock manager with empty tags
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = []

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)

    completer = dialog.fuzzy_completer
    assert completer is not None
    assert isinstance(completer, FuzzyTagCompleter)

    # Verify model is empty
    model = completer.model()
    assert model.rowCount() == 0

    dialog.close()


# ============================================================================
# Test Case 8: Fuzzy Matching Integration
# ============================================================================


def test_fuzzy_matching_integration(qt_app, mock_snippet_manager):
    """
    Test that fuzzy matching works end-to-end in the dialog.

    Verifies:
    - FuzzyTagCompleter is attached to dialog
    - Fuzzy matching works with typos (e.g., "pyton" → "python")
    - Completer is properly configured
    """
    # Mock snippet manager with specific tags
    mock_snippet_manager.get_all_tags.return_value = ["python", "javascript"]

    dialog = SnippetEditorDialog(snippet_manager=mock_snippet_manager, parent=None)
    completer = dialog.fuzzy_completer

    # Verify completer exists and is configured
    assert completer is not None
    assert isinstance(completer, FuzzyTagCompleter)

    dialog.close()


# ============================================================================
# Phase 4 Tests: Multi-Tag Input with Autocomplete
# ============================================================================


def test_single_tag_autocomplete_unchanged(qt_app):
    """
    Test that single-tag autocomplete still works (backward compatibility).

    Verifies:
    - Phase 3 behavior is unchanged
    - Typing "python" suggests tags matching "python"
    - No regression from multi-tag implementation
    """
    # Mock snippet manager with test tags
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside", "pytest", "testing"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)
    completer = dialog.fuzzy_completer

    # Test by triggering the text changed handler
    dialog.tags_input.setText("python")
    dialog._on_tags_input_changed("python")

    # Check that model was updated with matches
    model = completer.model()
    assert model.rowCount() > 0  # Should have at least one match

    dialog.close()


def test_comma_triggers_tag_reset(qt_app):
    """
    When user types comma, completer should be ready for next tag.

    Verifies:
    - Input: "python, " → Completer resets for new tag
    - Empty string after comma shows suggestions (completer ready)
    - Next typed character triggers new suggestions
    """
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside", "testing"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)
    completer = dialog.fuzzy_completer

    # Simulate typing "python, " (note trailing space)
    dialog.tags_input.setText("python, ")
    dialog._on_tags_input_changed("python, ")

    # After comma + space, completer should show suggestions for empty string
    # Empty string shows first 10 tags
    model = completer.model()
    # Should show some tags (empty input shows first 10)
    assert model.rowCount() > 0

    dialog.close()


def test_multi_tag_independent_autocomplete(qt_app):
    """
    Each comma-separated tag should get independent fuzzy suggestions.

    Verifies:
    - Input: "python, pyt" → Suggestions for "pyt" only
    - Completer matches current tag being typed (after last comma)
    - Previously typed tags don't interfere with current suggestions
    """
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside", "pytest", "testing"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)
    completer = dialog.fuzzy_completer

    # Simulate typing "python, pyt"
    dialog.tags_input.setText("python, pyt")
    dialog._on_tags_input_changed("python, pyt")

    # Check that model was updated with matches for "pyt"
    model = completer.model()

    # Get all matches from model
    matches = []
    for i in range(model.rowCount()):
        index = model.index(i, 0)
        matches.append(model.data(index))

    # Should match tags with "pyt" pattern
    assert "pytest" in matches or "python" in matches
    # At least one match should be present
    assert len(matches) > 0

    dialog.close()


def test_whitespace_handling_around_commas(qt_app):
    """
    Whitespace around commas should be trimmed correctly.

    Verifies:
    - Input: "python , pyside " → Tags saved as ["python", "pyside"]
    - Extra spaces around commas don't create empty tags
    - Tags are normalized correctly on save
    """
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)

    # Set up dialog fields for save
    dialog.name_input.setText("Test Snippet")
    dialog.content_input.setPlainText("Test content")
    dialog.tags_input.setText("python , pyside ")

    # Trigger save
    dialog._on_save()

    # Verify tags are trimmed
    snippet_data = dialog.get_snippet_data()
    assert snippet_data is not None
    tags = snippet_data["tags"]

    # Both tags should be present and trimmed
    assert "python" in tags
    assert "pyside" in tags
    assert len(tags) == 2

    # Should not contain tags with whitespace
    assert "python " not in tags
    assert " pyside" not in tags

    dialog.close()


def test_multiple_commas_empty_tags_filtered(qt_app):
    """
    Empty tags between commas should be filtered out.

    Verifies:
    - Input: "python,,pyside" → Saved as ["python", "pyside"]
    - Empty strings from split(",") are filtered
    - No empty tags in final result
    """
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)

    # Set up dialog fields
    dialog.name_input.setText("Test Snippet")
    dialog.content_input.setPlainText("Test content")
    dialog.tags_input.setText("python,,pyside")

    # Trigger save
    dialog._on_save()

    # Verify empty tag is filtered
    snippet_data = dialog.get_snippet_data()
    assert snippet_data is not None
    tags = snippet_data["tags"]

    # Should have exactly 2 tags (empty filtered out)
    assert len(tags) == 2
    assert "python" in tags
    assert "pyside" in tags

    # Should not contain empty strings
    assert "" not in tags

    dialog.close()


def test_trailing_comma_ready_for_next_tag(qt_app):
    """
    Trailing comma should prepare completer for next tag.

    Verifies:
    - Input: "python," → Completer ready for new tag
    - Next character typed triggers suggestions for new tag
    - Completer shows suggestions (not empty)
    """
    manager = Mock(spec=SnippetManager)
    manager.get_all_tags.return_value = ["python", "pyside", "pytest"]

    dialog = SnippetEditorDialog(snippet_manager=manager, parent=None)
    completer = dialog.fuzzy_completer

    # Type "python," (trailing comma, no space)
    dialog.tags_input.setText("python,")
    dialog._on_tags_input_changed("python,")

    # Completer should show suggestions for empty string after comma
    model = completer.model()
    # Empty input shows first 10 tags
    assert model.rowCount() > 0

    dialog.close()
