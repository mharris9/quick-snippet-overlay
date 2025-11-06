"""Test autocomplete setup."""
import sys
from PySide6.QtWidgets import QApplication
from src.snippet_manager import SnippetManager
from src.config_manager import ConfigManager
from src.snippet_editor_dialog import SnippetEditorDialog

app = QApplication(sys.argv)

# Load tags
cm = ConfigManager()
sm = SnippetManager(cm.get('snippet_file'))
sm.load()
tags = sm.get_all_tags()

print(f"[OK] Loaded {len(tags)} tags: {tags[:5]}...")

# Create dialog
dialog = SnippetEditorDialog(sm)

# Check if completer is set up
if hasattr(dialog, 'fuzzy_completer'):
    print("[OK] fuzzy_completer exists")
    print(f"  Completer mode: {dialog.fuzzy_completer.completionMode()}")
    print(f"  Max visible: {dialog.fuzzy_completer.maxVisibleItems()}")
else:
    print("[FAIL] fuzzy_completer NOT found!")

if hasattr(dialog, 'all_tags'):
    print(f"[OK] all_tags exists ({len(dialog.all_tags)} tags)")
else:
    print("[FAIL] all_tags NOT found!")

# Check if tags_input has completer
completer = dialog.tags_input.completer()
if completer:
    print("[OK] tags_input has completer attached")
else:
    print("[FAIL] tags_input has NO completer!")

# Test typing
print("\nSimulating typing 'p'...")
dialog.tags_input.setText("p")
dialog._on_tags_input_changed("p")

print("\nDialog is ready. Opening...")
dialog.show()
sys.exit(app.exec())
