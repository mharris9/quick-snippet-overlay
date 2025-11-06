# Phase 3: Tag Autocomplete - Fuzzy Matching Enhancement

## Execution Prompt

---

## Project Context

**Project**: Quick Snippet Overlay v1.0
**Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay`
**Status**: Phase 2 complete - Basic QCompleter integration functional
**Language**: Python 3.x with PySide6
**Test Suite**: 112 tests (91 passing, 5 failing, 16 errors - pre-existing issues)

Quick Snippet Overlay is a Windows 11 desktop application that provides instant text snippet access via global hotkey. Phase 1 added `get_all_tags()` backend support. Phase 2 integrated Qt's QCompleter for basic autocomplete. Phase 3 enhances the autocomplete with fuzzy matching for typo tolerance.

---

## Phase 2 Completion Status

✅ **Completed**:
- `SnippetEditorDialog` accepts optional `snippet_manager` parameter (src/snippet_editor_dialog.py:26)
- `_setup_completer()` method implemented (src/snippet_editor_dialog.py:97-108)
- QCompleter attached to tags_input with:
  - Case-insensitive matching (Qt.CaseInsensitive)
  - Popup completion mode (QCompleter.PopupCompletion)
  - Populated from SnippetManager.get_all_tags()
- 7 new tests added and passing:
  - `test_completer_exists`
  - `test_completer_attached_to_tags_input`
  - `test_completer_model_populated_on_init`
  - `test_completer_case_insensitive`
  - `test_completer_popup_mode`
  - `test_no_completer_when_manager_is_none`
  - `test_completer_with_empty_tags`
- No regressions in existing tests (91/112 passing, same as before)
- Code formatted with black

**Current Behavior**: Basic substring matching works (type "pyt" shows "python"), but typos don't work ("pyton" shows nothing).

---

## Phase 3 Objective

Replace Qt's basic substring matching with fuzzy matching using rapidfuzz, enabling typo-tolerant tag suggestions (e.g., "pyton" → "python").

---

## Tasks for Phase 3

### Task 1: Create FuzzyTagCompleter Class

**File**: `src/fuzzy_tag_completer.py` (NEW)

**Requirements**:

1. **Create custom QCompleter subclass**:
   ```python
   from PySide6.QtWidgets import QCompleter
   from PySide6.QtCore import Qt
   from rapidfuzz import fuzz
   from typing import List

   class FuzzyTagCompleter(QCompleter):
       """Custom QCompleter with fuzzy matching for tag suggestions."""

       def __init__(self, tags: List[str], parent=None):
           """
           Initialize fuzzy tag completer.

           Args:
               tags: List of existing tags to suggest
               parent: Parent widget (optional)
           """
           super().__init__(tags, parent)
           self.tags = tags
           self.score_cutoff = 60  # Match SearchEngine threshold

           # Configure base completer
           self.setCaseSensitivity(Qt.CaseInsensitive)
           self.setCompletionMode(QCompleter.PopupCompletion)
   ```

2. **Override splitPath() for fuzzy matching**:
   ```python
   def splitPath(self, path: str) -> List[str]:
       """
       Override to provide fuzzy-matched suggestions.

       Args:
           path: Current input text

       Returns:
           List of matching tags (fuzzy sorted by score)
       """
       if not path:
           return []

       # Get fuzzy matches with scores
       matches = []
       for tag in self.tags:
           score = fuzz.ratio(path.lower(), tag.lower())
           if score >= self.score_cutoff:
               matches.append((tag, score))

       # Sort by score (descending), then alphabetically
       matches.sort(key=lambda x: (-x[1], x[0]))

       # Return top 10 matches (limit suggestions)
       return [tag for tag, score in matches[:10]]
   ```

3. **Add method to update tags**:
   ```python
   def update_tags(self, tags: List[str]):
       """
       Update the list of tags for fuzzy matching.

       Args:
           tags: New list of existing tags
       """
       self.tags = tags

       # Update the completer's model
       from PySide6.QtCore import QStringListModel
       self.setModel(QStringListModel(tags))
   ```

**Edge Cases to Handle**:
- Empty input → return empty list (no suggestions)
- No tags match threshold → return empty list
- Single character input → still fuzzy match
- Exact match exists → prioritize it (score = 100)

---

### Task 2: Write Tests for FuzzyTagCompleter

**File**: `tests/test_fuzzy_tag_completer.py` (NEW)

**Required Tests**:

1. **`test_exact_match`**
   - Setup: FuzzyTagCompleter with tags ["python", "javascript", "testing"]
   - Action: splitPath("python")
   - Expected: ["python"] (exact match, score=100)

2. **`test_typo_tolerance`**
   - Setup: FuzzyTagCompleter with ["python", "javascript"]
   - Action: splitPath("pyton")
   - Expected: ["python"] (fuzzy match despite missing 'h')

3. **`test_prefix_match`**
   - Setup: FuzzyTagCompleter with ["python", "pyside", "pyqt", "javascript"]
   - Action: splitPath("py")
   - Expected: Contains "python", "pyside", "pyqt" (all match prefix)

4. **`test_no_match_below_threshold`**
   - Setup: FuzzyTagCompleter with ["python", "javascript"]
   - Action: splitPath("xyz")
   - Expected: [] (no tags score above 60)

5. **`test_case_insensitive_matching`**
   - Setup: FuzzyTagCompleter with ["Python", "JavaScript"]
   - Action: splitPath("PYTHON")
   - Expected: ["Python"] (case-insensitive)

6. **`test_score_sorting`**
   - Setup: FuzzyTagCompleter with ["python", "pyside", "testing"]
   - Action: splitPath("pyt")
   - Expected: "python" comes before "pyside" (better score)

7. **`test_empty_input`**
   - Setup: FuzzyTagCompleter with ["python"]
   - Action: splitPath("")
   - Expected: [] (no suggestions for empty input)

8. **`test_limit_suggestions`**
   - Setup: FuzzyTagCompleter with 20 tags starting with "test-"
   - Action: splitPath("test")
   - Expected: Returns max 10 suggestions (not all 20)

9. **`test_update_tags_method`**
   - Setup: FuzzyTagCompleter with ["old-tag"]
   - Action: update_tags(["new-tag"]), then splitPath("new")
   - Expected: ["new-tag"] (model updated)

**Testing Approach**:
- Follow TDD: Write tests FIRST (red)
- Implement FuzzyTagCompleter (green)
- Verify tests pass (refactor)

**Test Fixtures**:
```python
import pytest
from src.fuzzy_tag_completer import FuzzyTagCompleter

@pytest.fixture
def basic_tags():
    """Common tag list for testing."""
    return ["python", "javascript", "testing", "pyside", "pyqt"]

@pytest.fixture
def completer(basic_tags):
    """FuzzyTagCompleter instance with basic tags."""
    return FuzzyTagCompleter(basic_tags)
```

---

### Task 3: Integrate FuzzyTagCompleter into SnippetEditorDialog

**File**: `src/snippet_editor_dialog.py`

**Modifications**:

1. **Update imports**:
   ```python
   # Change from:
   from PySide6.QtWidgets import QCompleter

   # To:
   from src.fuzzy_tag_completer import FuzzyTagCompleter
   ```

2. **Modify `_setup_completer()` method**:
   ```python
   def _setup_completer(self):
       """Setup fuzzy autocomplete for tag input field."""
       if not self.snippet_manager:
           return

       tags = self.snippet_manager.get_all_tags()

       # Use FuzzyTagCompleter instead of QCompleter
       completer = FuzzyTagCompleter(tags, self)

       self.tags_input.setCompleter(completer)
   ```

**Changes**:
- Replace `QCompleter(tags, self)` with `FuzzyTagCompleter(tags, self)`
- Remove manual configuration (FuzzyTagCompleter does it internally)
- Keep same behavior for when `snippet_manager` is None

---

### Task 4: Update Tests for FuzzyTagCompleter Integration

**File**: `tests/test_snippet_editor_dialog.py`

**Modifications**:

1. **Update imports**:
   ```python
   from src.fuzzy_tag_completer import FuzzyTagCompleter
   ```

2. **Modify existing test: `test_completer_exists`**:
   ```python
   def test_completer_exists(dialog_with_manager):
       """Test that FuzzyTagCompleter is created when snippet_manager is provided."""
       completer = dialog_with_manager.tags_input.completer()
       assert completer is not None
       assert isinstance(completer, FuzzyTagCompleter)  # Changed from QCompleter
   ```

3. **Modify existing test: `test_completer_attached_to_tags_input`**:
   ```python
   def test_completer_attached_to_tags_input(dialog_with_manager):
       """Test that FuzzyTagCompleter is correctly attached to tags_input."""
       tags_input = dialog_with_manager.tags_input
       completer = tags_input.completer()

       assert completer is not None
       assert isinstance(completer, FuzzyTagCompleter)  # Changed from QCompleter
   ```

4. **Add new test: `test_fuzzy_matching_integration`**:
   ```python
   def test_fuzzy_matching_integration(qt_app, mock_snippet_manager):
       """Test that fuzzy matching works end-to-end in the dialog."""
       # Mock snippet manager with specific tags
       mock_snippet_manager.get_all_tags.return_value = ["python", "javascript"]

       dialog = SnippetEditorDialog(snippet_manager=mock_snippet_manager, parent=None)
       completer = dialog.tags_input.completer()

       # Test fuzzy match (typo tolerance)
       matches = completer.splitPath("pyton")
       assert "python" in matches

       dialog.close()
   ```

**No Changes Needed**:
- `test_completer_model_populated_on_init` - Still valid
- `test_completer_case_insensitive` - Still valid
- `test_completer_popup_mode` - Still valid
- `test_no_completer_when_manager_is_none` - Still valid
- `test_completer_with_empty_tags` - Still valid

---

## Technical Context

### Current Implementation (Phase 2)

**File**: `src/snippet_editor_dialog.py` (lines 97-108)

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

**Limitation**: Qt's default QCompleter uses simple substring matching. "pyton" won't match "python".

### Fuzzy Matching Strategy

**Using rapidfuzz.fuzz.ratio()**:
- Levenshtein distance-based scoring (0-100)
- 100 = exact match
- 60+ = reasonable match (same as SearchEngine)
- Example: `fuzz.ratio("pyton", "python")` ≈ 91

**Why override splitPath()?**:
- Qt calls `splitPath()` to determine suggestions
- Default implementation: simple string split
- Custom implementation: fuzzy match and score

**Performance**:
- rapidfuzz is already used in SearchEngine (tested, fast)
- Typical tag count: <100 tags
- Fuzzy matching: <10ms latency (acceptable)

---

## Success Criteria

- [ ] `FuzzyTagCompleter` class created in `src/fuzzy_tag_completer.py`
- [ ] `splitPath()` method uses rapidfuzz for fuzzy matching
- [ ] Score cutoff = 60 (matches SearchEngine)
- [ ] Limit = 10 suggestions max
- [ ] `update_tags()` method allows refreshing tag list
- [ ] 9 new tests written for FuzzyTagCompleter
- [ ] All 9 new tests passing
- [ ] `SnippetEditorDialog` uses FuzzyTagCompleter instead of QCompleter
- [ ] 2 existing dialog tests updated (instance checks)
- [ ] 1 new integration test added
- [ ] No regressions in existing tests (91/112 passing maintained)
- [ ] Code formatted with `black src/ tests/`

---

## Commands to Run

**Run FuzzyTagCompleter tests**:
```powershell
pytest tests/test_fuzzy_tag_completer.py -v
```

**Run dialog tests** (verify integration):
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

### Step 1: Write FuzzyTagCompleter Tests (Red)
```powershell
# Create: tests/test_fuzzy_tag_completer.py
# Add: All 9 tests
pytest tests/test_fuzzy_tag_completer.py -v
# Expected: ALL FAIL (class doesn't exist yet)
```

### Step 2: Implement FuzzyTagCompleter (Green)
```powershell
# Create: src/fuzzy_tag_completer.py
# Add: FuzzyTagCompleter class with splitPath() override
pytest tests/test_fuzzy_tag_completer.py -v
# Expected: ALL PASS
```

### Step 3: Update SnippetEditorDialog (Green)
```powershell
# Edit: src/snippet_editor_dialog.py
# Change: QCompleter → FuzzyTagCompleter
# Edit: tests/test_snippet_editor_dialog.py
# Update: 2 tests, add 1 new test
pytest tests/test_snippet_editor_dialog.py -v
# Expected: ALL PASS (including updated tests)
```

### Step 4: Verify No Regressions
```powershell
pytest
# Expected: 121 total tests (112 + 9 new)
# Expected: ~100 passing (same pass rate as before)
# Check: No NEW failures beyond pre-existing issues
```

### Step 5: Format Code
```powershell
black src/ tests/
```

---

## Edge Cases to Handle

1. **Empty tags list** → FuzzyTagCompleter created but shows no suggestions
2. **Empty input** → splitPath("") returns []
3. **Single character** → Still fuzzy match (e.g., "p" → ["python", "pyside"])
4. **No matches above threshold** → Return [] (no suggestions)
5. **Exact match exists** → Prioritize exact match (score=100)
6. **Many matches** → Limit to 10 suggestions
7. **Case variations** → Case-insensitive matching (inherited from Qt)

---

## Expected File Changes

### Files Created
- `src/fuzzy_tag_completer.py` - FuzzyTagCompleter class (~60 lines)
- `tests/test_fuzzy_tag_completer.py` - 9 tests (~150 lines)

### Files Modified
- `src/snippet_editor_dialog.py` - Replace QCompleter with FuzzyTagCompleter (~5 lines changed)
- `tests/test_snippet_editor_dialog.py` - Update 2 tests, add 1 new test (~30 lines)

### Files NOT Modified (Phase 3)
- `src/snippet_manager.py` - Already has `get_all_tags()` from Phase 1
- Any other files

---

## Testing Strategy

### Unit Tests (FuzzyTagCompleter Isolation)
- Test `splitPath()` with various inputs
- Test score calculation and filtering
- Test limit enforcement (max 10)
- Test case insensitivity
- Test empty/edge cases

### Integration Tests (With SnippetEditorDialog)
- Test dialog creates FuzzyTagCompleter instance
- Test end-to-end fuzzy matching through dialog
- Test backward compatibility (no snippet_manager)

### Manual Testing (After Implementation)
- Open snippet editor dialog
- Type partial tag with typo (e.g., "pyton")
- Verify dropdown appears with "python"
- Use arrow keys to navigate
- Press Enter to select
- Verify tag inserted into field

---

## Performance Considerations

**Fuzzy Matching Performance**:
- rapidfuzz.fuzz.ratio() is highly optimized (C extension)
- Typical tag count: 10-100 tags
- Worst case: 100 tags × fuzzy match = ~5ms
- Acceptable latency: <10ms (user won't notice)

**Optimization Notes**:
- No caching needed (tag count small)
- No indexing needed (linear scan is fast)
- Limit to 10 suggestions prevents UI clutter

**Benchmark Test** (Optional):
```python
def test_fuzzy_matching_performance():
    """Verify fuzzy matching completes in <10ms for 100 tags."""
    import time

    # Create 100 tags
    tags = [f"tag-{i:03d}" for i in range(100)]
    completer = FuzzyTagCompleter(tags)

    start = time.perf_counter()
    matches = completer.splitPath("tag")
    elapsed = time.perf_counter() - start

    assert elapsed < 0.01  # 10ms threshold
    assert len(matches) <= 10  # Limit enforced
```

---

## Notes for Phase 4

**Phase 4** will:
- Add multi-tag input support (comma-separated)
- Handle autocomplete for each tag independently
- Reset completer after comma typed
- Trim whitespace around tags

For now (Phase 3), focus on:
- Fuzzy matching for single tag input
- Typo tolerance
- Score-based filtering and sorting

---

## Definition of Done

1. `FuzzyTagCompleter` class exists in `src/fuzzy_tag_completer.py`
2. 9 new tests written and passing in `tests/test_fuzzy_tag_completer.py`
3. `SnippetEditorDialog` uses `FuzzyTagCompleter` instead of `QCompleter`
4. 2 dialog tests updated for type checks
5. 1 new integration test added
6. No regressions in existing tests (91/112 passing maintained)
7. Code formatted with black
8. Fuzzy matching works: "pyton" → "python"
9. Ready to proceed to Phase 4 (multi-tag support)

---

## References

- **Implementation Plan**: `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md`
- **Phase 1 Completion**: Implemented `SnippetManager.get_all_tags()`
- **Phase 2 Completion**: Integrated basic QCompleter
- **Project Instructions**: `CLAUDE.md`
- **Testing Patterns**: See `tests/test_snippet_manager.py`, `tests/test_search_engine.py`
- **rapidfuzz Docs**: https://github.com/maxbachmann/RapidFuzz
- **Qt QCompleter Docs**: https://doc.qt.io/qtforpython-6/PySide6/QtWidgets/QCompleter.html

---

**Ready to Execute**: YES
**Estimated Time**: 45 minutes
**Complexity**: Medium
**Risk**: Low (isolated change, backward-compatible)

---

## Execute Command

To execute this phase:

```
Implement Phase 3 of tag autocomplete feature as specified in PHASE-3-TAG-AUTOCOMPLETE-PROMPT.md.

Follow TDD approach:
1. Create tests/test_fuzzy_tag_completer.py with 9 tests - verify they fail
2. Create src/fuzzy_tag_completer.py with FuzzyTagCompleter class
3. Implement splitPath() method using rapidfuzz for fuzzy matching
4. Verify all 9 new tests pass
5. Modify src/snippet_editor_dialog.py to use FuzzyTagCompleter
6. Update 2 existing tests in tests/test_snippet_editor_dialog.py
7. Add 1 new integration test
8. Run full test suite - verify no new regressions
9. Format code with black

Success criteria: All new tests pass, fuzzy matching works ("pyton" → "python"), no regressions.
```
