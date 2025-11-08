"""
Restore Backup Dialog - UI for restoring snippets from backup files

This module provides a dialog window for selecting and restoring from backup files.

Key features:
- Lists all available backups (rotation and manual)
- Shows backup names and timestamps
- Allows selection of backup to restore
- Confirms restore operation before proceeding
"""

from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt
from datetime import datetime


class RestoreBackupDialog(QDialog):
    """
    Dialog for selecting and restoring from backup files.

    Usage:
        backups = snippet_manager.list_backups()
        dialog = RestoreBackupDialog(backups, parent=window)
        if dialog.exec():
            selected_backup = dialog.selected_backup
            snippet_manager.restore_from_backup(selected_backup)
    """

    def __init__(self, backups: list, parent=None):
        """
        Initialize restore backup dialog.

        Args:
            backups: List of backup dicts with 'path', 'name', 'timestamp' keys
            parent: Parent widget (optional)
        """
        super().__init__(parent)

        self.backups = backups
        self.selected_backup = None

        self._setup_ui()
        self._apply_styles()

    def _setup_ui(self):
        """Setup the dialog UI."""
        self.setWindowTitle("Restore from Backup")
        self.setModal(True)
        self.resize(500, 400)

        # Main layout
        layout = QVBoxLayout()
        layout.setSpacing(15)

        # Header label
        header = QLabel("Select a backup to restore:")
        header.setStyleSheet("font-size: 14px; font-weight: bold;")
        layout.addWidget(header)

        # Info label
        info = QLabel(
            "Restoring from a backup will replace your current snippets.\n"
            "Your current snippets will be backed up automatically before restoring."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #999999; font-size: 11px;")
        layout.addWidget(info)

        # Backup list
        self.backup_list = QListWidget()
        self.backup_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.backup_list.itemDoubleClicked.connect(self._on_restore)

        # Populate backup list
        for backup in self.backups:
            # Format timestamp
            timestamp_str = datetime.fromtimestamp(backup["timestamp"]).strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            # Create list item
            item_text = f"{backup['name']}\n  Created: {timestamp_str}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, backup["path"])

            self.backup_list.addItem(item)

        layout.addWidget(self.backup_list)

        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        # Restore button
        self.restore_button = QPushButton("Restore")
        self.restore_button.setFixedWidth(100)
        self.restore_button.clicked.connect(self._on_restore)
        self.restore_button.setEnabled(False)  # Disabled until selection
        button_layout.addWidget(self.restore_button)

        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Connect selection changed signal
        self.backup_list.itemSelectionChanged.connect(self._on_selection_changed)

    def _apply_styles(self):
        """Apply dark theme styles."""
        self.setStyleSheet(
            """
            QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QLabel {
                color: #ffffff;
            }
            QListWidget {
                background-color: #1e1e1e;
                color: #ffffff;
                border: 1px solid #3d3d3d;
                padding: 5px;
                font-size: 12px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #3d3d3d;
            }
            QListWidget::item:selected {
                background-color: #094771;
            }
            QListWidget::item:hover {
                background-color: #3d3d3d;
            }
            QPushButton {
                background-color: #0e639c;
                color: #ffffff;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #1177bb;
            }
            QPushButton:pressed {
                background-color: #094771;
            }
            QPushButton:disabled {
                background-color: #3d3d3d;
                color: #777777;
            }
        """
        )

    def _on_selection_changed(self):
        """Handle backup selection change."""
        selected_items = self.backup_list.selectedItems()
        self.restore_button.setEnabled(len(selected_items) > 0)

    def _on_restore(self):
        """Handle restore button click or double-click on item."""
        selected_items = self.backup_list.selectedItems()
        if not selected_items:
            return

        # Get selected backup path
        selected_item = selected_items[0]
        backup_path = selected_item.data(Qt.ItemDataRole.UserRole)
        backup_name = selected_item.text().split("\n")[0]

        # Confirm restore
        reply = QMessageBox.question(
            self,
            "Confirm Restore",
            f"Are you sure you want to restore from:\n\n{backup_name}\n\n"
            f"Your current snippets will be backed up automatically before restoring.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.selected_backup = backup_path
            self.accept()
