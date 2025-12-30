# Quick Snippet Overlay

A Windows 11 desktop application that provides instant access to text snippets via a global hotkey. Built with Python and PySide6.

![Status](https://img.shields.io/badge/status-v1.0-green)
![Coverage](https://img.shields.io/badge/coverage-85%25-brightgreen)
![Tests](https://img.shields.io/badge/tests-156%2F166%20passing-brightgreen)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Global Hotkey Access** - Press `Ctrl+Shift+Space` to instantly open the snippet overlay
- **Fuzzy Search** - Find snippets quickly with typo-tolerant search powered by rapidfuzz
- **Variable Substitution** - Use `{{variable_name:default_value}}` for dynamic content
- **Quick Add Snippets** - Add snippets with `Ctrl+N` or the `+` button (no YAML editing required)
- **Mass Delete** - Delete multiple snippets with filtering (`Ctrl+D` or 🗑️ button)
- **Tag Autocomplete** - Smart tag suggestions with fuzzy matching
- **Auto-Reload** - Changes to snippet file automatically refresh without restart
- **Multi-Monitor Support** - Overlay appears on the monitor with your cursor
- **Draggable Window** - Reposition the overlay anywhere on screen
- **System Tray Integration** - Access features from the system tray menu
- **Standalone Executable** - No Python installation required (47MB .exe)

## Screenshots

![Overlay Window](docs/screenshots/overlay.png)
*Fuzzy search overlay with keyboard navigation*

![Add Snippet Dialog](docs/screenshots/add-snippet.png)
*Simple GUI for creating new snippets*

## Quick Start

### Option 1: Standalone Executable (Recommended)

**No Python installation required!**

1. **Download** `QuickSnippetOverlay.exe` from the `dist/` folder
2. **Run** the executable by double-clicking it
3. **Check system tray** for the Quick Snippet Overlay icon
4. **Press `Ctrl+Shift+Space`** to open the overlay

That's it! The application will automatically create configuration and snippet files on first run.

### Option 2: Run from Source (Development)

**Prerequisites:**
- Windows 11 (or Windows 10 with compatible APIs)
- Python 3.11 or higher
- Git

**Installation:**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/mharris9/quick-snippet-overlay.git
   cd quick-snippet-overlay
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Install dependencies:**
   ```bash
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   .\RUN-APP.bat
   ```
   or
   ```bash
   .\RUN-APP.ps1
   ```

### First Launch

On first run, the application will:
- Create default snippet file at `C:\Users\YourName\snippets\snippets.yaml`
- Create config file at `C:\Users\YourName\snippets\config.yaml`
- Add sample snippets (PowerShell, Git, Python, LLM prompts)
- Start system tray icon

## Usage

### Opening the Overlay

- **Hotkey:** Press `Ctrl+Shift+Space` anywhere on Windows
- **System Tray:** Right-click tray icon → "Open Overlay"

### Searching Snippets

1. Type in the search box (fuzzy matching works!)
2. Use arrow keys to navigate results
3. Press `Enter` to copy snippet to clipboard
4. Press `Esc` to close overlay

### Adding Snippets

**GUI Method (Recommended):**
1. Right-click system tray icon
2. Click "Add Snippet..."
3. Fill in the form:
   - **Name:** Display name for the snippet
   - **Description:** Brief description for search
   - **Tags:** Comma-separated (auto-normalized)
   - **Content:** Paste or type your snippet
4. Click "Save Snippet"
5. Snippet immediately available!

**YAML Method (Advanced):**
1. Right-click system tray icon → "Edit Snippets"
2. Add snippet in YAML format:
   ```yaml
   - id: unique-id
     name: My Snippet
     description: Brief description
     content: |
       Your snippet content here
       Use {{variable_name:default_value}} for variables
     tags: [tag1, tag2]
     created: 2025-11-05
     modified: 2025-11-05
   ```
3. Save file (auto-reloads within 500ms)

### Using Variables

Create dynamic snippets with variables. Variable names can contain any characters except curly braces:

```yaml
content: |
  Hello {{name:World}},

  Your order #{{order_id:12345}} is ready.
  Total: ${{amount:0.00}}

  # Variables can use spaces and hyphens too:
  Branch: {{short-description}}
  Issue: {{Describe the bug}}
```

When selected, you'll be prompted to enter values for each variable (or use defaults).

## Configuration

Edit `C:\Users\YourName\snippets\config.yaml`:

```yaml
snippet_file: "C:/Users/YourName/snippets/snippets.yaml"
hotkey: "ctrl+shift+space"
overlay_width: 600
overlay_height: 400
overlay_opacity: 0.95
theme: "dark"
search_debounce_ms: 150
fuzzy_threshold: 60
max_results: 10
```

## Architecture

```
┌─────────────────────────────────────────┐
│          User Presses Hotkey            │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   HotkeyManager (pynput + Qt signals)   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  OverlayWindow (PySide6 frameless UI)   │
│  - Fuzzy search (rapidfuzz)              │
│  - Keyboard navigation                   │
│  - Multi-monitor positioning             │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   SnippetManager (YAML + watchdog)      │
│   - Auto-reload on file changes          │
│   - Backup rotation (5 backups)          │
│   - Schema validation                    │
└─────────────────────────────────────────┘
```

### Key Components

- **ConfigManager** - YAML config with validation and defaults
- **SnippetManager** - YAML loading, hot-reload, backup rotation
- **SearchEngine** - Weighted fuzzy search (name: 3x, description: 2x, tags: 2x, content: 1x)
- **OverlayWindow** - Frameless popup with drag support
- **SystemTray** - Menu integration with snippet editor
- **HotkeyManager** - Global hotkey via pynput with Qt signals
- **VariableHandler** - Variable detection and substitution
- **SnippetEditorDialog** - GUI form for creating snippets

## Development

### Running Tests

```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# View coverage report
start htmlcov/index.html
```

**Test Results:**
- 156/166 passing tests (94% pass rate)
- 85% code coverage overall
- 10 known test infrastructure failures (delete dialog mocking - functionality works correctly)
- Components: ConfigManager (97%), SearchEngine (98%), VariableHandler (92%), FuzzyTagCompleter (92%)

### Code Quality

```bash
# Format code
black src/ tests/

# Lint
pylint src/

# Sort imports
isort src/ tests/
```

### Project Structure

```
quick-snippet-overlay/
├── src/
│   ├── main.py                  # Entry point
│   ├── overlay_window.py        # Main UI
│   ├── system_tray.py           # Tray integration
│   ├── snippet_editor_dialog.py # Add snippet GUI
│   ├── snippet_manager.py       # YAML management
│   ├── search_engine.py         # Fuzzy search
│   ├── hotkey_manager.py        # Global hotkey
│   ├── config_manager.py        # Configuration
│   ├── variable_handler.py      # Variable substitution
│   └── variable_prompt_dialog.py # Variable input
├── tests/
│   └── test_*.py                # Test files
├── RUN-APP.bat                  # Windows launcher
├── RUN-APP.ps1                  # PowerShell launcher
├── CLEANUP-AND-RUN.bat          # Cleanup + restart
└── requirements.txt             # Python dependencies
```

## Troubleshooting

### Application Won't Start

**"Already Running" error:**
```bash
# Run cleanup script
.\CLEANUP-AND-RUN.bat
```

**Import errors:**
```bash
# Ensure virtual environment is activated
.\.venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt
```

### Overlay Not Appearing

1. Check system tray for icon
2. Right-click tray icon → "Open Overlay"
3. Verify hotkey not in use by another app
4. Check console for error messages

### Snippets Not Loading

1. Verify file exists: `C:\Users\YourName\snippets\snippets.yaml`
2. Check YAML syntax (use "Edit Snippets" to open in editor)
3. Review console logs for validation errors
4. Use "Reload Snippets" from tray menu

## Roadmap

**Phase 7 (Packaging) - ✅ Completed:**
- ✅ PyInstaller executable (47MB standalone)
- ✅ Production-ready build (debug logging removed)
- ✅ User documentation (README, USER-GUIDE)
- 📦 Inno Setup Windows installer (manual task)
- 📦 Application icon (.ico file - manual task)

**Future Enhancements:**
- Cloud sync for snippets
- Snippet categories/folders
- Custom themes (light mode)
- Snippet templates
- Hotkey customization UI
- Plugin system

## Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Write tests for new features
4. Ensure tests pass (`pytest`)
5. Format code (`black src/ tests/`)
6. Commit changes (`git commit -m 'Add amazing feature'`)
7. Push to branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) file for details

## Acknowledgments

- Built with [PySide6](https://www.qt.io/qt-for-python) (LGPL)
- Fuzzy search powered by [rapidfuzz](https://github.com/maxbachmann/RapidFuzz)
- File watching via [watchdog](https://github.com/gorakhargosh/watchdog)
- Global hotkeys via [pynput](https://github.com/moses-palmer/pynput)

## Support

- **Issues:** [GitHub Issues](https://github.com/mharris9/quick-snippet-overlay/issues)
- **Discussions:** [GitHub Discussions](https://github.com/mharris9/quick-snippet-overlay/discussions)

---

**Quick Snippet Overlay** - Instant access to your text snippets, powered by Python 🐍
