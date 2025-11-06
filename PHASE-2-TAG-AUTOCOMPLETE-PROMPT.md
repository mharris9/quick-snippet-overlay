# Phase 2: Tag Autocomplete - Basic QCompleter Integration

## Execution Prompt

---

## Project Context

**Project**: Quick Snippet Overlay v1.0
**Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay`
**Status**: Phase 1 complete - `get_all_tags()` method implemented and tested
**Language**: Python 3.x with PySide6
**Test Suite**: 105 tests (84 passing, 5 failing, 16 errors - pre-existing issues)

Quick Snippet Overlay is a Windows 11 desktop application that provides instant text snippet access via global hotkey. Phase 1 added backend support for retrieving unique tags. Phase 2 integrates Qt's QCompleter for basic tag autocomplete.

---

## Phase 1 Completion Status

✅ **Completed**:
- `SnippetManager.get_all_tags()` method implemented (src/snippet_manager.py:448-458)
- Returns deduplicated, sorted list of tags
- 4 new tests added and passing:
  - `test_get_all_tags_empty`
  - `test_get_all_tags_deduplicates`
  - `test_get_all_tags_sorted`
  - `test_get_all_tags_from_multiple_snippets`
- No regressions in snippet_manager tests (14/15 passing, 1 flaky performance test)
- Code formatted with black

---

## Phase 2 Objective

Attach Qt's QCompleter to the tag input field in the snippet editor dialog to provide basic autocomplete suggestions from existing tags.

---

## Tasks for Phase 2

### Task 1: Create Test File (if needed)

**File**: `tests/test_snippet_editor_dialog.py`

**Check**: Use Glob tool to verify if this file exists
- If exists: Read it to understand existing test structure
- If missing: Create new test file following project patterns

**Requirements**:
1. Import necessary modules:
   - `pytest`
   - `PySide6.QtWidgets` (QApplication, QCompleter)
   - `src.snippet_editor_dialog.SnippetEditorDialog`
   - `src.snippet_manager.SnippetManager`
2. Create fixtures if needed:
   - `qtbot` (from pytest-qt)
   - Mock snippet manager
3. Follow existing test patterns from other test files

---

### Task 2: Write Tests for Completer Integration (TDD - Red)

**File**: `tests/test_snippet_editor_dialog.py`

**Required Tests**:

1. **`test_completer_exists`**
   - Setup: Create SnippetEditorDialog instance
   - Action: Access `tags_input.completer()`
   - Expected: Completer is not None and is a QCompleter instance

2. **`test_completer_attached_to_tags_input`**
   - Setup: Create SnippetEditorDialog with mock snippet manager
   - Action: Check if completer is attached to `tags_input` field
   - Expected: `tags_input.completer()` returns valid QCompleter

3. **`test_completer_model_populated_on_init`**
   - Setup: Mock snippet manager with 3 tags: ["python", "javascript", "testing"]
   - Action: Create dialog, get completer model
   - Expected: Model contains all 3 tags in sorted order

4. **`test_completer_case_insensitive`**
   - Setup: Create dialog with completer
   - Action: Check completer case sensitivity setting
   - Expected: `completer.caseSensitivity() == Qt.CaseInsensitive`

5. **`test_completer_popup_mode`**
   - Setup: Create dialog with completer
   - Action: Check completer completion mode
   - Expected: `completer.completionMode() == QCompleter.PopupCompletion`

**Testing Approach**:
- Follow TDD: Write tests FIRST (red)
- Tests will fail initially (dialog doesn't have completer yet)
- Implement completer in Task 3 (green)
- Verify tests pass (refactor)

---

### Task 3: Modify SnippetEditorDialog to Add Completer

**File**: `src/snippet_editor_dialog.py`

**Requirements**:

1. **Add snippet_manager parameter to `__init__`**:
   ```python
   def __init__(self, snippet_manager=None, parent=None):
       """
       Initialize snippet editor dialog.

       Args:
           snippet_manager: SnippetManager instance for tag suggestions (optional)
           parent: Parent widget (optional)
       """
       super().__init__(parent)
       self.snippet_manager = snippet_manager
       self.snippet_data = None
       self._setup_ui()
       self._setup_completer()  # New method
   ```

2. **Create `_setup_completer()` method**:
   - Check if `snippet_manager` is provided
   - Get all tags using `snippet_manager.get_all_tags()`
   - Create `QCompleter` with tags list
   - Set case sensitivity to `Qt.CaseInsensitive`
   - Set completion mode to `QCompleter.PopupCompletion`
   - Attach to `self.tags_input` using `setCompleter()`

3. **Example implementation**:
   ```python
   def _setup_completer(self):
       """Setup autocomplete for tag input field."""
       if not self.snippet_manager:
           return

       tags = self.snippet_manager.get_all_tags()

       completer = QCompleter(tags, self)
       completer.setCaseSensitivity(Qt.CaseInsensitive)
       completer.setCompletionMode(QCompleter.PopupCompletion)

       self.tags_input.setCompleter(completer)
   ```

4. **Import additions needed**:
   ```python
   from PySide6.QtWidgets import QCompleter
   from PySide6.QtCore import Qt
   ```

**Edge Cases to Handle**:
- `snippet_manager` is `None` → Don't create completer (graceful degradation)
- Empty tags list → Completer still created but shows no suggestions
- Dialog used without snippet manager → Works as before (no autocomplete)

---

## Technical Context

### Current SnippetEditorDialog Structure

**File**: `src/snippet_editor_dialog.py`

**Key Components**:
```python
class SnippetEditorDialog(QDialog):
    def __init__(self, parent=None):
        self.snippet_data = None
        self._setup_ui()

    def _setup_ui(self):
        # Creates:
        # - self.name_input (QLineEdit)
        # - self.desc_input (QLineEdit)
        # - self.tags_input (QLineEdit) ← TARGET for completer
        # - self.content_input (QTextEdit)
        # - self.save_button (QPushButton)
        # - self.cancel_button (QPushButton)
```

**Tags Input Field** (line 61-64):
```python
tags_label = QLabel("Tags (comma-separated):")
self.tags_input = QLineEdit()
self.tags_input.setPlaceholderText("e.g., email, work, signature")
layout.addWidget(tags_label)
layout.addWidget(self.tags_input)
```

### How Other Components Use the Dialog

**File**: `src/system_tray.py` (likely location)

Expected usage pattern:
```python
# Before Phase 2:
dialog = SnippetEditorDialog(parent=self)

# After Phase 2:
dialog = SnippetEditorDialog(snippet_manager=self.snippet_manager, parent=self)
```

**Important**: Don't break existing usage! Make `snippet_manager` parameter optional with default `None`.

### PySide6 QCompleter Basics

**Setup Pattern**:
```python
from PySide6.QtWidgets import QCompleter, QLineEdit
from PySide6.QtCore import Qt

# Create completer with string list
completer = QCompleter(["tag1", "tag2", "tag3"], parent)

# Configure behavior
completer.setCaseSensitivity(Qt.CaseInsensitive)  # Ignore case
completer.setCompletionMode(QCompleter.PopupCompletion)  # Show dropdown

# Attach to line edit
line_edit.setCompleter(completer)
```

**User Experience**:
- User types in `tags_input` field
- Dropdown appears with matching suggestions
- User can arrow down/up to select
- Press Enter or Tab to insert selected suggestion
- Esc to dismiss dropdown
- Can continue typing to ignore suggestions

---

## Success Criteria

- [ ] `test_snippet_editor_dialog.py` created (if missing)
- [ ] All 5 new tests written and initially failing (RED)
- [ ] `SnippetEditorDialog.__init__` accepts `snippet_manager` parameter (optional)
- [ ] `_setup_completer()` method exists
- [ ] QCompleter attached to `tags_input` field
- [ ] Completer case sensitivity set to `CaseInsensitive`
- [ ] Completer mode set to `PopupCompletion`
- [ ] All 5 new tests passing (GREEN)
- [ ] No regressions in existing tests
- [ ] Code formatted with `black src/ tests/`

---

## Commands to Run

**Check if test file exists**:
```powershell
Get-ChildItem -Path tests -Filter "*snippet_editor*.py" -Recurse
```

**Run specific tests** (after writing them):
```powershell
pytest tests/test_snippet_editor_dialog.py -v
```

**Run all tests**:
```powershell
pytest
```

**Format code**:
```powershell
black src/ tests/
```

---

## Implementation Workflow (TDD)

### Step 1: Check for Existing Test File
```powershell
# Use Glob tool or bash
ls tests/test_snippet_editor*.py
# If missing: Create it in Step 2
# If exists: Read it first to understand structure
```

### Step 2: Write First Test (Red)
```powershell
# Edit: tests/test_snippet_editor_dialog.py
# Add: test_completer_exists()
pytest tests/test_snippet_editor_dialog.py::test_completer_exists -v
# Expected: FAIL (completer doesn't exist yet)
```

### Step 3: Write Remaining Tests (Red)
```powershell
# Edit: tests/test_snippet_editor_dialog.py
# Add: 4 more tests
pytest tests/test_snippet_editor_dialog.py -v
# Expected: ALL FAIL (completer not implemented)
```

### Step 4: Implement _setup_completer() (Green)
```powershell
# Edit: src/snippet_editor_dialog.py
# Add: snippet_manager parameter to __init__
# Add: _setup_completer() method
# Modify: __init__ to call _setup_completer()
pytest tests/test_snippet_editor_dialog.py -v
# Expected: ALL PASS
```

### Step 5: Verify No Regressions
```powershell
pytest
# Expected: 110 total tests (105 existing + 5 new)
# Check: No new failures beyond pre-existing issues
```

### Step 6: Format Code
```powershell
black src/ tests/
```

---

## Edge Cases to Handle

1. **snippet_manager is None** → No completer created (graceful)
2. **Empty tags list** → Completer created but shows no suggestions
3. **Single tag** → Completer shows 1 suggestion
4. **Many tags (100+)** → QCompleter handles efficiently (built-in filtering)
5. **Dialog instantiated without snippet_manager** → Works as before

---

## Expected File Changes

### Files Created (if needed)
- `tests/test_snippet_editor_dialog.py` - New test file (~100 lines)

### Files Modified
- `src/snippet_editor_dialog.py` - Add completer setup (~30 lines)

### Files NOT Modified (Phase 2)
- `src/snippet_manager.py` - Already has `get_all_tags()` from Phase 1
- Any other files

---

## Testing Strategy

### Unit Tests (Dialog in Isolation)
- Test completer exists
- Test completer attached to correct widget
- Test completer configured correctly
- Test model populated with tags

### Integration Tests (With SnippetManager)
- Test completer gets tags from snippet manager
- Test empty snippet manager case
- Test None snippet manager case

### Manual Testing (After Implementation)
- Open snippet editor dialog
- Type partial tag (e.g., "pyt")
- Verify dropdown appears with suggestions
- Use arrow keys to navigate
- Press Enter to select
- Verify tag inserted into field

---

## Notes for Next Phases

**Phase 3** will:
- Replace basic substring matching with fuzzy matching (rapidfuzz)
- Create custom `FuzzyTagCompleter` class
- Handle typos (e.g., "pyton" → "python")

**Phase 4** will:
- Add comma-separated tag support
- Autocomplete each tag independently
- Handle whitespace and normalization

For now (Phase 2), focus on:
- Basic QCompleter integration
- Connecting to snippet manager
- Simple substring matching (Qt's default)

---

## Definition of Done

1. `test_snippet_editor_dialog.py` exists (or created)
2. 5 new tests written and passing
3. `SnippetEditorDialog` accepts optional `snippet_manager` parameter
4. `_setup_completer()` method implemented
5. QCompleter attached and configured correctly
6. No regressions in existing tests
7. Code formatted with black
8. Ready to proceed to Phase 3 (fuzzy matching)

---

## References

- **Implementation Plan**: `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md`
- **Phase 1 Completion**: Implemented `SnippetManager.get_all_tags()`
- **Project Instructions**: `CLAUDE.md`
- **Testing Patterns**: See `tests/test_snippet_manager.py`, `tests/test_overlay_window.py`
- **PySide6 QCompleter Docs**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QCompleter.html

---

**Ready to Execute**: YES
**Estimated Time**: 30 minutes
**Complexity**: Low
**Risk**: Minimal (isolated change, backward-compatible)

---

## Execute Command

To execute this phase:

```
Implement Phase 2 of tag autocomplete feature as specified in PHASE-2-TAG-AUTOCOMPLETE-PROMPT.md.

Follow TDD approach:
1. Check if tests/test_snippet_editor_dialog.py exists
2. Create it if needed OR read existing structure
3. Write 5 tests for completer integration - verify they fail
4. Modify SnippetEditorDialog to add snippet_manager parameter
5. Implement _setup_completer() method with QCompleter
6. Verify all 5 new tests pass
7. Run full test suite - verify no new regressions
8. Format code with black

Success criteria: All 5 new tests pass, no new regressions, completer functional.
```
