# Phase 1: Tag Autocomplete - Core Infrastructure

## Execution Prompt

---

## Project Context

**Project**: Quick Snippet Overlay v1.0
**Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay`
**Status**: Production-ready, 101/101 tests passing, 92% coverage
**Language**: Python 3.x with PySide6

Quick Snippet Overlay is a Windows 11 desktop application that provides instant text snippet access via global hotkey. Users can create snippets with tags for organization. Currently, tags are manually entered, leading to potential proliferation of similar tags (e.g., "python", "Python", "py", "Python3").

---

## Feature Overview

**Goal**: Add fuzzy autocomplete to tag input in snippet editor to prevent tag proliferation.

**Full Implementation Plan**: `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md` (this directory)

**Current Phase**: Phase 1 of 5 - Core Infrastructure (30 min estimated)

---

## Phase 1 Objective

Add backend support for retrieving all unique tags from the snippet collection. This enables future phases to populate autocomplete suggestions.

---

## Tasks for Phase 1

### Task 1: Implement `get_all_tags()` Method

**File**: `src/snippet_manager.py`

**Requirements**:
1. Add method `get_all_tags(self) -> List[str]`
2. Extract all tags from `self.snippets` list
3. Return deduplicated, sorted list
4. Handle edge cases:
   - Empty snippets list → return `[]`
   - Snippets with no tags → skip them
   - Duplicate tags → deduplicate
   - Mixed case → already normalized to lowercase by existing code

**Implementation Notes**:
- Each snippet has a `tags` field (List[str])
- Tags are already normalized to lowercase with spaces→dashes
- Use Python set for deduplication, then sort

**Example**:
```python
# Given snippets:
# Snippet 1: tags=["python", "code"]
# Snippet 2: tags=["python", "testing"]
# Snippet 3: tags=["javascript"]

# get_all_tags() should return:
# ["code", "javascript", "python", "testing"]
```

---

### Task 2: Write Tests

**File**: `tests/test_snippet_manager.py`

**Required Tests**:

1. **`test_get_all_tags_empty`**
   - Setup: SnippetManager with no snippets
   - Action: Call `get_all_tags()`
   - Expected: Returns `[]`

2. **`test_get_all_tags_deduplicates`**
   - Setup: Multiple snippets with duplicate tags
   - Action: Call `get_all_tags()`
   - Expected: Returns deduplicated list

3. **`test_get_all_tags_sorted`**
   - Setup: Snippets with tags in random order
   - Action: Call `get_all_tags()`
   - Expected: Returns alphabetically sorted list

4. **`test_get_all_tags_from_multiple_snippets`**
   - Setup: 3+ snippets with overlapping tags
   - Action: Call `get_all_tags()`
   - Expected: Returns union of all tags (deduplicated, sorted)

**Testing Approach**:
- Follow TDD: Write tests FIRST (red)
- Implement method (green)
- Verify tests pass (refactor)

---

## Technical Context

### Current SnippetManager Structure

**File**: `src/snippet_manager.py`

**Key Attributes**:
```python
class SnippetManager:
    def __init__(self, snippet_file: Path):
        self.snippet_file = snippet_file
        self.snippets: List[Snippet] = []  # List of loaded snippets
        # ... other attributes
```

**Snippet Dataclass**:
```python
@dataclass
class Snippet:
    id: str
    name: str
    description: str
    content: str
    tags: List[str]  # Already normalized (lowercase, spaces→dashes)
    created: str
    modified: str
```

### Existing Test Patterns

**File**: `tests/test_snippet_manager.py`

**Example Test Structure**:
```python
def test_something(tmp_path, mocker):
    """Test description."""
    # Setup
    snippet_file = tmp_path / "snippets.yaml"
    manager = SnippetManager(snippet_file)

    # Action
    result = manager.some_method()

    # Assert
    assert result == expected_value
```

**Fixtures Available** (in `conftest.py`):
- `tmp_path` - Temporary directory
- `mocker` - pytest-mock for mocking
- `sample_snippets_file` - Pre-created YAML file with snippets

---

## Success Criteria

- [ ] `get_all_tags()` method exists in `src/snippet_manager.py`
- [ ] Method returns `List[str]`
- [ ] Empty snippets → returns `[]`
- [ ] Duplicate tags → returns deduplicated list
- [ ] Tags are sorted alphabetically
- [ ] All 4 new tests written and passing
- [ ] All existing 101 tests still pass (zero regressions)
- [ ] Code formatted with `black src/ tests/`
- [ ] Coverage maintained at ≥92% (run `pytest --cov=src`)

---

## Commands to Run

**Activate Virtual Environment** (Windows PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

**Run Specific Tests** (after writing them):
```powershell
pytest tests/test_snippet_manager.py::test_get_all_tags_empty -v
pytest tests/test_snippet_manager.py::test_get_all_tags_deduplicates -v
pytest tests/test_snippet_manager.py::test_get_all_tags_sorted -v
pytest tests/test_snippet_manager.py::test_get_all_tags_from_multiple_snippets -v
```

**Run All Tests**:
```powershell
pytest
```

**Check Coverage**:
```powershell
pytest --cov=src --cov-report=html
```

**Format Code**:
```powershell
black src/ tests/
```

---

## Implementation Workflow (TDD)

### Step 1: Write First Test (Red)
```powershell
# Edit: tests/test_snippet_manager.py
# Add: test_get_all_tags_empty()
pytest tests/test_snippet_manager.py::test_get_all_tags_empty -v
# Expected: FAIL (method doesn't exist yet)
```

### Step 2: Implement Method Stub (Red → Green)
```powershell
# Edit: src/snippet_manager.py
# Add: def get_all_tags(self) -> List[str]: return []
pytest tests/test_snippet_manager.py::test_get_all_tags_empty -v
# Expected: PASS (for empty case)
```

### Step 3: Write Remaining Tests (Red)
```powershell
# Edit: tests/test_snippet_manager.py
# Add: test_get_all_tags_deduplicates(), test_get_all_tags_sorted(), etc.
pytest tests/test_snippet_manager.py -k "get_all_tags" -v
# Expected: Some FAIL (stub implementation incomplete)
```

### Step 4: Complete Implementation (Green)
```powershell
# Edit: src/snippet_manager.py
# Complete: get_all_tags() logic (extract, dedupe, sort)
pytest tests/test_snippet_manager.py -k "get_all_tags" -v
# Expected: ALL PASS
```

### Step 5: Verify No Regressions (Refactor)
```powershell
pytest
# Expected: 105/105 tests passing (101 existing + 4 new)
```

### Step 6: Format Code
```powershell
black src/ tests/
```

---

## Edge Cases to Handle

1. **Empty snippets list** → `[]`
2. **Snippet with empty tags field** → Skip it
3. **All snippets have same tags** → Return unique tags once
4. **Tags already sorted in snippets** → Still sort result
5. **Single snippet** → Return its tags (deduplicated if it has duplicates)

---

## Expected File Changes

### Files Modified
- `src/snippet_manager.py` - Add `get_all_tags()` method (~10 lines)
- `tests/test_snippet_manager.py` - Add 4 tests (~60 lines)

### Files NOT Modified (Phase 1)
- `src/snippet_editor_dialog.py` - Not yet (Phase 2)
- Any other files

---

## Definition of Done

1. `get_all_tags()` method implemented and working
2. All 4 new tests written and passing
3. All 101 existing tests still passing (105 total)
4. Code formatted with black
5. Coverage ≥92% maintained
6. No lint errors
7. Ready to proceed to Phase 2

---

## Next Steps After Phase 1

Once Phase 1 is complete:
- Phase 2 will integrate QCompleter into snippet editor dialog
- Phase 3 will add fuzzy matching with rapidfuzz
- Phase 4 will handle comma-separated tags
- Phase 5 will be final integration testing

See `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md` for full roadmap.

---

## Questions or Issues?

Refer to:
- **Architecture**: `HANDOFF-ADVANCED-FEATURES.md`
- **Project Instructions**: `CLAUDE.md`
- **Testing Patterns**: `tests/test_snippet_manager.py` (existing tests)
- **Full Implementation Plan**: `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md`

---

**Ready to Execute**: YES
**Estimated Time**: 30 minutes
**Complexity**: Low
**Risk**: Minimal (isolated change, well-tested)

---

## Execute Command

To execute this phase:

```
Implement Phase 1 of tag autocomplete feature as specified in PHASE-1-TAG-AUTOCOMPLETE-PROMPT.md.

Follow TDD approach:
1. Write test_get_all_tags_empty() - verify it fails
2. Add get_all_tags() stub to SnippetManager - verify test passes
3. Write remaining 3 tests - verify they fail
4. Complete get_all_tags() implementation - verify all tests pass
5. Run full test suite - verify no regressions (105 tests total)
6. Format code with black

Success criteria: All 4 new tests pass, 101 existing tests pass, coverage ≥92%.
```
