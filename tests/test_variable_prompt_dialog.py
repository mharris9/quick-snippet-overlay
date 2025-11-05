"""
Tests for variable_prompt_dialog.py - Variable input modal dialogs

Test Coverage:
1. Dialog creation and display
2. Default value pre-population
3. OK button returns user value
4. Cancel button aborts operation
5. Empty input validation
6. Sequential prompts for multiple variables
7. Cancel during sequential prompts aborts entire operation
"""

import pytest
import sys
from unittest.mock import Mock, patch


@pytest.fixture(scope="module")
def qt_app():
    """Create QApplication instance for testing."""
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import QCoreApplication

    # Check if an instance already exists using QCoreApplication
    existing_app = QCoreApplication.instance()
    if existing_app is not None:
        yield existing_app
    else:
        # Create new QApplication
        app_instance = QApplication(sys.argv if sys.argv else [])
        yield app_instance


def test_dialog_shows_variable_name(qt_app):
    """Test dialog displays correct variable name in label."""
    from src.variable_prompt_dialog import VariablePromptDialog

    dialog = VariablePromptDialog("filepath", default_value=None)

    # Verify the label contains the variable name
    assert dialog.label.text() == "Enter value for: filepath"


def test_dialog_prepopulates_default_value(qt_app):
    """Test dialog pre-populates input field with default value."""
    from src.variable_prompt_dialog import VariablePromptDialog

    dialog = VariablePromptDialog("port", default_value="5000")

    # Verify input field contains default value
    assert dialog.input_field.text() == "5000"


def test_dialog_ok_button_returns_value(qt_app):
    """Test OK button returns user-entered value."""
    from src.variable_prompt_dialog import VariablePromptDialog

    dialog = VariablePromptDialog("test_var")

    # Simulate user entering value
    dialog.input_field.setText("test_value")
    dialog.value = "test_value"

    # Simulate accepting the dialog (without exec)
    dialog.accept()

    # Verify value was set correctly
    assert dialog.value == "test_value"


def test_dialog_cancel_button_returns_none(qt_app):
    """Test Cancel button returns None."""
    from src.variable_prompt_dialog import VariablePromptDialog
    from PySide6.QtCore import QTimer

    dialog = VariablePromptDialog("test_var")

    # Simulate user clicking Cancel
    QTimer.singleShot(10, dialog.reject)
    result = dialog.get_value()

    assert result is None


def test_dialog_empty_input_shows_error(qt_app):
    """Test empty input shows 'This field is required' error."""
    from src.variable_prompt_dialog import VariablePromptDialog
    from PySide6.QtWidgets import QMessageBox
    from unittest.mock import patch

    dialog = VariablePromptDialog("test_var")
    dialog.input_field.setText("")  # Empty input

    # Mock QMessageBox to prevent actual dialog from showing
    with patch.object(QMessageBox, 'warning') as mock_warning:
        dialog._on_ok()

        # Verify warning was shown
        mock_warning.assert_called_once()
        assert "required" in mock_warning.call_args[0][2].lower()


def test_sequential_prompts_for_multiple_variables(qt_app):
    """Test multiple variables prompt sequentially."""
    from src.variable_prompt_dialog import prompt_for_variables
    from unittest.mock import patch, MagicMock

    variables = [
        {'name': 'var1', 'default': None},
        {'name': 'var2', 'default': 'default2'}
    ]

    # Mock the dialog to return values without showing UI
    with patch('src.variable_prompt_dialog.VariablePromptDialog') as MockDialog:
        mock_dialog1 = MagicMock()
        mock_dialog1.get_value.return_value = "value1"

        mock_dialog2 = MagicMock()
        mock_dialog2.get_value.return_value = "value2"

        MockDialog.side_effect = [mock_dialog1, mock_dialog2]

        result = prompt_for_variables(variables)

        assert result == {'var1': 'value1', 'var2': 'value2'}
        assert MockDialog.call_count == 2


def test_cancel_during_sequential_prompts_aborts(qt_app):
    """Test Cancel mid-sequence aborts entire operation."""
    from src.variable_prompt_dialog import prompt_for_variables
    from unittest.mock import patch, MagicMock

    variables = [
        {'name': 'var1', 'default': None},
        {'name': 'var2', 'default': None},
        {'name': 'var3', 'default': None}
    ]

    # Mock the dialog: first returns value, second returns None (cancel), third never called
    with patch('src.variable_prompt_dialog.VariablePromptDialog') as MockDialog:
        mock_dialog1 = MagicMock()
        mock_dialog1.get_value.return_value = "value1"

        mock_dialog2 = MagicMock()
        mock_dialog2.get_value.return_value = None  # User cancelled

        MockDialog.side_effect = [mock_dialog1, mock_dialog2]

        result = prompt_for_variables(variables)

        # Operation should abort and return None
        assert result is None
        # Only 2 dialogs should have been created (3rd never shown)
        assert MockDialog.call_count == 2
