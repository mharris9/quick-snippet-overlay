# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Project Overview

**Quick Snippet Overlay** is a Windows 11 desktop application that provides instant access to text snippets via a global hotkey. Built with Python and PySide6, it features fuzzy search, variable substitution, tag autocomplete, system tray integration, and hot-reload capabilities.

**Current Status**: Phase 5 complete - Tag Autocomplete with Advanced Focus Management - All features functional

---

## Essential Commands

### Development Environment

```powershell
# Activate virtual environment (REQUIRED before running any commands)
.\.venv\Scripts\Activate.ps1

# Run the application
python src/main.py

# Run application with PowerShell script (handles venv activation)
.\RUN-APP.ps1
```

### Testing

```powershell
# Run all tests
pytest

# Run all tests with coverage report
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/test_snippet_manager.py

# Run specific test function
pytest tests/test_overlay_window.py::TestOverlayWindow::test_show_overlay

# Run tests with verbose output
pytest -v

# Run tests with timeout (prevents hangs)
pytest --timeout=10
```

### Code Quality

```powershell
# Format code with black
black src/ tests/

# Lint with pylint
pylint src/

# Sort imports
isort src/ tests/
```

---

## Architecture Overview

### Component Communication Flow

```
User Presses Hotkey (Ctrl+Shift+Space)
    ↓
HotkeyManager (pynput thread) emits Qt signal
    ↓
main.py toggle_overlay() callback
    ↓
OverlayWindow shows and centers on active monitor
    ↓
User types search query → SearchEngine (fuzzy search with rapidfuzz)
    ↓
User selects snippet → VariableHandler detects {{variables}}
    ↓
(If variables) VariablePromptDialog shows sequential prompts
    ↓
Content copied to clipboard (pyperclip)
    ↓
OverlayWindow hides after 500ms
```

### Core Components

**Data Layer** (`snippet_manager.py`):
- Loads/validates YAML snippets with schema validation
- Watches file for changes with 500ms debounce (watchdog)
- Auto-fixes duplicate IDs (appends -1, -2, etc.)
- Maintains backup rotation (up to 5 backups)
- Falls back to last good state on YAML errors

**Search Layer** (`search_engine.py`):
- Fuzzy search using rapidfuzz (Levenshtein distance)
- Weighted scoring: name (3x), description (2x), tags (2x), content (1x)
- Threshold filtering (default: 60/100)
- Results sorted by relevance

**Variable System** (`variable_handler.py`, `variable_prompt_dialog.py`):
- Detects `{{variable_name:default_value}}` syntax
- Sequential dialog prompts (one variable at a time)
- Substitutes variables before clipboard copy
- Cancel returns to overlay without closing

**UI Layer** (`overlay_window.py`):
- Frameless, always-on-top Qt window
- Multi-monitor support (centers on screen with mouse cursor)
- Real-time search with 150ms debounce
- Keyboard navigation (arrows, Enter, ESC)
- Dark theme with configurable opacity

**Snippet Editor** (`snippet_editor_dialog.py`, `fuzzy_tag_completer.py`):
- Add/Edit snippet dialog with form validation
- **Tag Autocomplete System** - Advanced fuzzy matching with focus preservation:
  - Continuous typing without clicking (fixed OS-level window activation bug)
  - Tab key autocomplete (selects first match)
  - Click selection from dropdown
  - Enter key selection
  - ESC key dismissal
  - Tool window type prevents keyboard event stealing
  - Custom NoFocusListView rejects activation events
  - Multi-tag comma-separated input support
- Fuzzy tag matching (prefix → substring → typo-tolerant)
- Real-time dropdown updates

**Integration** (`system_tray.py`, `hotkey_manager.py`, `main.py`):
- System tray with context menu (Show/Edit Snippets/Settings/Quit)
- Global hotkey registration via pynput (thread-safe Qt signals)
- Single instance enforcement (lock file with PID validation)
- Graceful shutdown with cleanup handlers

**Configuration** (`config_manager.py`):
- YAML-based configuration with defaults
- Schema validation
- Hot-reload on file changes (watchdog)
- Validation errors trigger fallback to defaults

---

## Key Design Patterns

### Thread Safety
- **HotkeyManager** runs in pynput thread, uses Qt signals to communicate with main thread
- All UI updates happen in Qt main thread only
- Watchdog file observers emit callbacks safely

### Error Handling
- **SnippetManager**: Falls back to last good state on YAML errors
- **ConfigManager**: Falls back to defaults on validation errors
- **OverlayWindow**: Shows error dialogs for clipboard/variable failures
- **main.py**: Single instance enforcement with stale lock file cleanup

### Testing Strategy
- **Unit tests**: Mock external dependencies (QApplication, pynput, file I/O)
- **Integration tests**: Test component interactions with minimal mocks
- **Edge cases**: Empty inputs, malformed YAML, duplicate IDs, missing files
- **Coverage target**: 85% per component, 90% overall (achieved: 92%)

---

## Critical Implementation Details

### PySide6 vs PyQt6
**Current**: PySide6 6.10.0 (LGPL license)
- Phases 5-6 initially used PyQt6, migrated to PySide6 for licensing
- `.claude/CLAUDE.md` documents compliance verification process
- See `PYQT6-VS-PYSIDE6-ANALYSIS.md` for technical comparison

### Overlay Window Multi-Monitor Support
Uses `QApplication.screenAt(QCursor.pos())` to detect active monitor and center window there. Falls back to primary screen if detection fails.

### Hotkey Parsing Limitations
Current `HotkeyManager._parse_hotkey()` only supports `ctrl+shift+space` pattern. Extending to other combinations requires updating `_is_hotkey_pressed()` logic.

### Variable Substitution Order
Variables are prompted in the order they appear in the snippet content. Same variable can appear multiple times - only prompted once.

### Debouncing Strategy
- **Search input**: 150ms debounce using QTimer (configurable)
- **File watching**: 500ms debounce using time.time() comparison
- Prevents performance issues with rapid input/file changes

### Lock File Handling
Lock file stored at `~/.quick-snippet-overlay/app.lock` with current PID. On startup:
1. Check if lock file exists
2. Read PID and verify process still running (Windows: `kernel32.OpenProcess`)
3. If stale, remove lock file and continue
4. If active, show error and exit
5. Register `atexit` cleanup handler

### Tag Autocomplete Focus Management
Critical fix for Windows OS-level window activation stealing keyboard events:
- **Problem**: `Qt.WindowType.Popup` windows activate at OS level, routing keyboard to popup instead of tags_input
- **Solution**: Use `Qt.WindowType.Tool` (never becomes active window)
- **Implementation**:
  - `NoFocusListView` with `Tool | FramelessWindowHint | WindowStaysOnTopHint`
  - Reject `WindowActivate`, `ActivationChange`, `FocusIn` events
  - Explicit focus restoration after popup.show() with `processEvents()`
  - Event filter handles Tab/Enter/ESC keys for selection and dismissal
- **Result**: User can type continuously without clicking back into field
- **Ref**: `FOCUS-FIX-BREAKTHROUGH.md` for detailed technical analysis

---

## Testing Conventions

### Fixture Organization
- `conftest.py`: Shared fixtures (qtbot, temp directories, sample snippets)
- `fixtures/`: Sample YAML files for testing

### Test Naming
```python
# Pattern: test_{component}_{action}_{condition}
def test_snippet_manager_load_with_missing_file()
def test_search_engine_fuzzy_matching_with_typos()
def test_overlay_window_keyboard_navigation_with_arrow_keys()
```

### Mock Usage
```python
# Mock Qt application (required for all UI tests)
mocker.patch('src.overlay_window.QApplication.instance', return_value=mock_app)

# Mock file operations
mocker.patch('pathlib.Path.exists', return_value=True)

# Mock pynput (HotkeyManager tests)
mocker.patch('src.hotkey_manager.keyboard.Listener')
```

---

## Configuration Files

### `config.yaml` (User Configuration)
```yaml
snippet_file: "C:/Users/mikeh/.quick-snippet-overlay/snippets.yaml"
hotkey: "ctrl+shift+space"
overlay_width: 600
overlay_height: 400
overlay_opacity: 0.95
theme: "dark"
search_debounce_ms: 150
fuzzy_threshold: 60
max_results: 10
```

### `snippets.yaml` (Snippet Storage)
```yaml
version: 1
snippets:
  - id: unique-id
    name: Display Name
    description: Search description
    content: |
      Snippet content here
      Variables: {{var_name:default_value}}
    tags: [tag1, tag2]
    created: 2025-11-04
    modified: 2025-11-04
```

---

## Common Development Tasks

### Adding a New Snippet Field
1. Update `Snippet` dataclass in `snippet_manager.py`
2. Update `_parse_snippets()` to handle new field
3. Update `_validate_schema()` if field is required
4. Update `SearchEngine._calculate_snippet_score()` if searchable
5. Update sample file in `_create_sample_file()`
6. Add tests for new field

### Changing Hotkey Behavior
1. Modify `HotkeyManager._parse_hotkey()` to parse new key combinations
2. Update `_is_hotkey_pressed()` to detect new combinations
3. Add tests for new combinations in `test_hotkey_manager.py`
4. Update documentation/config examples

### Adding New Configuration Option
1. Add field to `ConfigManager.DEFAULT_CONFIG`
2. Update `_validate_config()` if validation needed
3. Access via `config.get('option_name', default_value)` in components
4. Add tests in `test_config_manager.py`

---

## Known Issues & Limitations

### Acceptable (v1.0)
- `main.py` coverage: 82% (difficult to unit test entry point)
- Performance test timing: Occasionally fails (timing-dependent)
- Settings dialog: Placeholder only (not functional)

### Future Enhancements (v1.1+)
- Cloud sync for snippets
- Snippet categories/folders
- Custom themes (light mode)
- Snippet templates
- Hotkey customization UI

---

## Phase Completion Workflow

**CRITICAL**: Before completing any phase, MUST run compliance verification (Step 13):
1. Copy `.claude/PHASE-COMPLIANCE-CHECKLIST.md` to `PHASE-{N}-COMPLIANCE-REVIEW.md`
2. Verify technology stack matches PRD
3. Verify all functional requirements implemented
4. Document discrepancies (P0/P1/P2)
5. Get user approval
6. Only then write completion report

See `.claude/CLAUDE.md` for detailed enforcement protocol.

---

## Dependencies

**Core**:
- PySide6 6.10.0 (LGPL) - UI framework
- rapidfuzz 3.14.3 (MIT) - Fuzzy search
- PyYAML 6.0.3 (MIT) - Configuration/data storage
- pyperclip 1.11.0 (BSD) - Clipboard integration
- pynput 1.8.1 (LGPL) - Global hotkey capture
- watchdog 6.0.0 (Apache 2.0) - File watching
- pywin32 311 (PSF) - Windows API integration

**Testing**:
- pytest 8.4.2 (MIT)
- pytest-cov 7.0.0 (MIT)
- pytest-mock 3.15.1 (MIT)
- pytest-qt 4.5.0 (MIT)
- pytest-timeout 2.4.0 (MIT)

**Development**:
- black 25.9.0 - Code formatting
- pylint 4.0.2 - Linting
- isort 7.0.0 - Import sorting

---

## Project Structure

```
quick-snippet-overlay/
├── src/
│   ├── main.py                  # Entry point, single instance, component wiring
│   ├── snippet_manager.py       # YAML loading, validation, file watching, backups
│   ├── search_engine.py         # Fuzzy search with weighted scoring
│   ├── variable_handler.py      # Variable detection and substitution
│   ├── variable_prompt_dialog.py # Sequential variable input dialogs
│   ├── overlay_window.py        # Frameless search UI, multi-monitor support
│   ├── system_tray.py           # System tray integration
│   ├── hotkey_manager.py        # Global hotkey registration (pynput)
│   └── config_manager.py        # Configuration management
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── test_*.py                # Test files (mirror src/)
│   └── fixtures/                # Sample YAML files
├── .claude/
│   ├── CLAUDE.md                # Project-specific instructions (this location)
│   └── PHASE-*.md               # Phase completion templates
├── requirements.txt             # Python dependencies
└── PHASE-*-COMPLETION-REPORT.md # Phase documentation
```

---

## Next Phase: Phase 7 - Packaging

**Objective**: Create Windows installer and distributable executable

**Key Tasks**:
1. PyInstaller configuration (.spec file)
2. Application icon (.ico)
3. Inno Setup installer script
4. User documentation (README, USER-GUIDE)
5. Performance optimization
6. Final integration testing

See `NEXT-STEPS.md` for detailed Phase 7 plan.

---

## Quick Reference

**Run app**: `python src/main.py` (after activating venv)
**Run tests**: `pytest`
**Coverage**: `pytest --cov=src --cov-report=html`
**Format**: `black src/ tests/`
**PRD location**: `C:\Users\mikeh\software_projects\brainstorming\PRD-quick-snippet-overlay-v2.md`
**Phase docs**: `PHASE-{N}-COMPLETION-REPORT.md`
