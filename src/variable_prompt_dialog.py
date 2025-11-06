"""
Variable Prompt Dialog - Modal dialogs for variable input

This module provides UI components for prompting users to enter values for
snippet variables during the copy operation.

Classes:
    VariablePromptDialog: Modal dialog for single variable input

Functions:
    prompt_for_variables: Show sequential prompts for multiple variables
"""

from typing import List, Optional, Dict
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt


class VariablePromptDialog(QDialog):
    """
    Modal dialog for prompting user to enter a variable value.

    Features:
    - Shows variable name in label
    - Pre-populates default value if provided
    - Validates non-empty input
    - Returns None on cancel, value on OK
    """

    def __init__(
        self, variable_name: str, default_value: Optional[str] = None, parent=None
    ):
        """
        Initialize variable prompt dialog.

        Args:
            variable_name: Name of the variable to prompt for
            default_value: Optional default value to pre-populate
            parent: Parent widget for modal behavior
        """
        super().__init__(parent)
        self.variable_name = variable_name
        self.default_value = default_value
        self.value = None
        self._setup_ui()

    def _setup_ui(self):
        """Create and configure UI components."""
        self.setWindowTitle("Variable Input")
        self.setModal(True)
        self.setFixedSize(400, 150)

        # Main layout
        layout = QVBoxLayout()

        # Label showing "Enter value for: {variable_name}"
        self.label = QLabel(f"Enter value for: {self.variable_name}")
        self.label.setStyleSheet("font-size: 12pt;")
        layout.addWidget(self.label)

        # Input field with default value
        self.input_field = QLineEdit()
        if self.default_value:
            self.input_field.setText(self.default_value)
        self.input_field.setFocus()
        self.input_field.setPlaceholderText("Enter value...")
        layout.addWidget(self.input_field)

        # Spacer
        layout.addStretch()

        # Button layout (Cancel, OK)
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        self.ok_button.clicked.connect(self._on_ok)
        button_layout.addWidget(self.ok_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _on_ok(self):
        """Validate input and accept if non-empty."""
        value = self.input_field.text().strip()
        if not value:
            QMessageBox.warning(
                self, "Error", "This field is required. Please enter a value."
            )
            return

        self.value = value
        self.accept()

    def get_value(self) -> Optional[str]:
        """
        Execute dialog and return user-entered value.

        Returns:
            User-entered value if OK clicked, None if cancelled
        """
        result = self.exec()
        if result == QDialog.DialogCode.Accepted:
            return self.value
        return None


def prompt_for_variables(
    variables: List[Dict[str, Optional[str]]], parent=None
) -> Optional[Dict[str, str]]:
    """
    Show sequential prompts for each variable.

    Args:
        variables: List of dicts with 'name' and optional 'default' keys
            Example: [{'name': 'filepath', 'default': None}, {'name': 'port', 'default': '5000'}]
        parent: Parent widget for modal dialogs

    Returns:
        Dict mapping variable names to user-entered values, or None if user cancels any prompt

    Example:
        >>> variables = [{'name': 'path', 'default': None}, {'name': 'port', 'default': '8080'}]
        >>> values = prompt_for_variables(variables)
        >>> if values:
        ...     print(values)  # {'path': '/home/user', 'port': '8080'}
    """
    values = {}

    for var in variables:
        var_name = var["name"]
        var_default = var.get("default")

        dialog = VariablePromptDialog(var_name, var_default, parent)
        value = dialog.get_value()

        if value is None:
            # User cancelled - abort entire operation
            return None

        values[var_name] = value

    return values
