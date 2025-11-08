"""Debug script to test overlay show_overlay and _update_results methods"""
import sys
from PySide6.QtWidgets import QApplication
from src.config_manager import ConfigManager
from src.snippet_manager import SnippetManager
from src.search_engine import SearchEngine
from src.variable_handler import VariableHandler
from src.overlay_window import OverlayWindow

# Create application
app = QApplication(sys.argv)

# Create components
config = ConfigManager()
snippet_manager = SnippetManager(config.get("snippet_file"))
snippets = snippet_manager.load()
search_engine = SearchEngine(snippets)
variable_handler = VariableHandler()

# Create overlay
overlay = OverlayWindow(config, snippet_manager, search_engine, variable_handler)

# Debug output
print(f"=== DEBUG INFO ===")
print(f"Total snippets loaded: {len(snippet_manager.snippets)}")
print(f"Snippet names: {[s.name for s in snippet_manager.snippets]}")
print(f"\nCalling show_overlay()...")

# Show overlay
overlay.show_overlay()

print(f"Overlay visible: {overlay.isVisible()}")
print(f"Overlay geometry: x={overlay.x()}, y={overlay.y()}, w={overlay.width()}, h={overlay.height()}")
print(f"Results list count: {overlay.results_list.count()}")
if overlay.results_list.count() > 0:
    print(f"First result: {overlay.results_list.item(0).text()}")
else:
    print("No results in list!")

# Keep app running
sys.exit(app.exec())
