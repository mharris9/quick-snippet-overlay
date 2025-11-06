# Tag Autocomplete - Implementation Plan

**Feature**: Fuzzy autocomplete for tag input in snippet editor
**Goal**: Prevent tag proliferation by suggesting existing tags as user types
**Estimated Time**: 2.5 hours
**Difficulty**: Low

---

## Overview

Add fuzzy autocomplete to tag input field in snippet editor, preventing tag proliferation by suggesting existing tags as user types. Uses existing rapidfuzz library for typo-tolerant matching.

---

## Phase Breakdown

### **Phase 1: Core Infrastructure** (30 min)

**Objective**: Add backend support for retrieving all unique tags

**Tasks**:
1. Add `get_all_tags()` method to `SnippetManager`
   - Returns `List[str]` of unique tags (sorted, lowercase)
   - Extracts from all snippets in memory
   - Updates when snippets reload

2. Write tests for `get_all_tags()`
   - Empty snippets list → empty tags
   - Multiple snippets with duplicate tags → deduplicated
   - Tags already normalized (existing behavior verified)

**Files Modified**:
- `src/snippet_manager.py` - Add method
- `tests/test_snippet_manager.py` - Add tests

**Success Criteria**:
- [ ] `get_all_tags()` method exists and returns `List[str]`
- [ ] Empty snippets → returns `[]`
- [ ] Duplicate tags → returns deduplicated list
- [ ] Tags are sorted alphabetically
- [ ] All existing tests still pass
- [ ] New tests pass

---

### **Phase 2: Basic QCompleter Integration** (30 min)

**Objective**: Attach Qt's QCompleter to tag input field

**Tasks**:
1. Modify `snippet_editor_dialog.py`
   - Create `QCompleter` instance
   - Attach to `tags_input` QLineEdit
   - Set completion mode: `PopupCompletion`
   - Set case sensitivity: `CaseInsensitive`

2. Connect to snippet manager
   - Populate completer on dialog init
   - Listen to `snippets_reloaded` signal
   - Update completer model when snippets change

3. Write tests for completer setup
   - Completer attached to input field
   - Model populated with existing tags
   - Updates on snippet reload

**Files Modified**:
- `src/snippet_editor_dialog.py` - Add completer
- `tests/test_snippet_editor_dialog.py` - Add tests (or create if missing)

**Success Criteria**:
- [ ] QCompleter attached to tag input
- [ ] Completer shows existing tags on init
- [ ] Completer updates when snippets reload
- [ ] All existing tests still pass
- [ ] New tests pass

---

### **Phase 3: Fuzzy Matching Enhancement** (45 min)

**Objective**: Replace basic substring matching with fuzzy matching

**Tasks**:
1. Create custom `FuzzyTagCompleter` class
   - Inherits from `QCompleter`
   - Override `splitPath()` to use rapidfuzz
   - Score threshold: 60 (matches existing search engine)
   - Limit: 10 suggestions

2. Replace basic completer with fuzzy version
   - Instantiate `FuzzyTagCompleter` instead of `QCompleter`
   - Pass existing tags list for fuzzy matching

3. Write tests for fuzzy matching
   - Exact match: "python" → ["python"]
   - Typo tolerance: "pyton" → ["python"]
   - Prefix match: "py" → ["python", "pyside", "pyqt"]
   - No match: "xyz" → []

**Files Created**:
- `src/fuzzy_tag_completer.py` - New class
- `tests/test_fuzzy_tag_completer.py` - New tests

**Files Modified**:
- `src/snippet_editor_dialog.py` - Use FuzzyTagCompleter

**Success Criteria**:
- [ ] FuzzyTagCompleter class exists
- [ ] Typo tolerance works (e.g., "pyton" → "python")
- [ ] Prefix matching works (e.g., "py" → multiple tags)
- [ ] Score threshold filters irrelevant matches
- [ ] All existing tests still pass
- [ ] New tests pass

---

### **Phase 4: Multi-Tag Input Support** (30 min)

**Objective**: Support comma-separated tags with autocomplete for each

**Tasks**:
1. Handle comma-separated tags
   - Detect when user types comma
   - Reset completer for next tag
   - Trim whitespace around tags

2. Real-time normalization preview (optional enhancement)
   - Show tooltip/hint: "My Tag" → "my-tag"
   - Uses existing `_normalize_tag()` logic

3. Write tests for multi-tag behavior
   - Multiple tags: "python, pyside" → both autocomplete
   - Whitespace handling: "python , pyside" → normalized
   - Completer resets after comma

**Files Modified**:
- `src/snippet_editor_dialog.py` - Add comma handling
- `tests/test_snippet_editor_dialog.py` - Add tests

**Success Criteria**:
- [ ] Comma triggers autocomplete reset
- [ ] Each tag gets independent autocomplete
- [ ] Whitespace trimmed correctly
- [ ] All existing tests still pass
- [ ] New tests pass

---

### **Phase 5: Integration Testing** (15 min)

**Objective**: Verify end-to-end functionality

**Tasks**:
1. Manual testing workflow
   - Open snippet editor (new snippet)
   - Type partial tag → verify dropdown appears
   - Select with keyboard → verify inserts
   - Type multiple tags → verify comma handling
   - Save snippet → verify tags normalized

2. Regression testing
   - Run full test suite (`pytest`)
   - Verify 0 broken tests
   - Coverage target: maintain ≥92%

**Success Criteria**:
- [ ] Manual testing passes all scenarios
- [ ] All 101+ existing tests pass
- [ ] Coverage ≥92% maintained
- [ ] No regressions detected

---

## Technical Details

### New Components

```
src/
└── fuzzy_tag_completer.py          # New: Custom QCompleter with rapidfuzz

tests/
└── test_fuzzy_tag_completer.py     # New: Completer tests
```

### Modified Components

```
src/
├── snippet_manager.py              # Add: get_all_tags() method
└── snippet_editor_dialog.py        # Modify: Attach completer to tags_input

tests/
├── test_snippet_manager.py         # Add: get_all_tags() tests
└── test_snippet_editor_dialog.py   # Add: Completer integration tests (or create if missing)
```

### Dependencies

- **No new dependencies** (reuse existing rapidfuzz 3.14.3)
- Existing: PySide6 6.10.0 (QCompleter, QStringListModel)

---

## Implementation Approach (TDD)

1. **Write test for `SnippetManager.get_all_tags()`** (Red)
2. **Implement `get_all_tags()` method** (Green)
3. **Verify test passes** (Refactor)
4. **Create `FuzzyTagCompleter` class with tests** (Red)
5. **Implement fuzzy matching logic** (Green)
6. **Verify fuzzy tests pass** (Refactor)
7. **Modify `snippet_editor_dialog.py` to integrate completer** (Red → Green)
8. **Write integration tests for dialog** (Red → Green)
9. **Verify all tests pass** (Refactor)
10. **Manual testing with real snippets**
11. **Update documentation (CLAUDE.md, docstrings)**

---

## Testing Strategy

### Unit Tests (New)

**SnippetManager** (`tests/test_snippet_manager.py`):
- `test_get_all_tags_empty` - Empty snippets → []
- `test_get_all_tags_deduplicates` - Duplicate tags → unique list
- `test_get_all_tags_sorted` - Returns alphabetically sorted
- `test_get_all_tags_from_multiple_snippets` - Aggregates across snippets

**FuzzyTagCompleter** (`tests/test_fuzzy_tag_completer.py`):
- `test_exact_match` - "python" → ["python"]
- `test_typo_tolerance` - "pyton" → ["python"]
- `test_prefix_match` - "py" → ["python", "pyside", "pyqt"]
- `test_no_match_below_threshold` - "xyz" → []
- `test_score_cutoff_respected` - Low scores filtered out

### Integration Tests (New)

**SnippetEditorDialog** (`tests/test_snippet_editor_dialog.py`):
- `test_completer_attached_to_tags_input`
- `test_completer_populated_with_existing_tags`
- `test_completer_updates_on_snippet_reload`
- `test_comma_separated_tags_autocomplete`

### Regression Tests (Existing)

- All 101 existing tests must still pass
- Coverage must remain ≥92%

---

## Expected Outcomes

### Functionality
- ✅ Tag input shows dropdown with suggestions as user types
- ✅ Fuzzy matching tolerates typos (e.g., "pyton" → "python")
- ✅ Comma-separated tags each get autocomplete
- ✅ Existing tags prevent proliferation of similar tags

### Code Quality
- ✅ Coverage: Maintain ≥92% overall
- ✅ Tests: ~10-12 new tests, all passing
- ✅ Zero regressions in existing 101 tests
- ✅ Code formatted with black, passes pylint

### User Experience
- ✅ Instant feedback (<10ms latency)
- ✅ Keyboard-friendly (arrow keys + Enter)
- ✅ Non-intrusive (can ignore suggestions)
- ✅ Case-insensitive matching

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| **QCompleter interferes with comma handling** | Test multi-tag input explicitly; override key events if needed |
| **Fuzzy matching too aggressive** | Use score_cutoff=60 (same as search engine) |
| **Performance with 1000+ tags** | rapidfuzz handles this easily; add benchmark test if needed |
| **Breaks existing tag normalization** | Regression tests ensure normalization still works |
| **Dialog tests don't exist yet** | Create `test_snippet_editor_dialog.py` if missing |

---

## Time Estimate

| Phase | Time |
|-------|------|
| Phase 1: Infrastructure | 30 min |
| Phase 2: Basic Completer | 30 min |
| Phase 3: Fuzzy Matching | 45 min |
| Phase 4: Multi-Tag Support | 30 min |
| Phase 5: Integration Testing | 15 min |
| **Total** | **~2.5 hours** |

---

## Success Criteria (Overall)

- [ ] `SnippetManager.get_all_tags()` returns deduplicated, sorted tags
- [ ] Tag input shows dropdown when typing partial tag
- [ ] Fuzzy matching suggests "python" when typing "pyton"
- [ ] Multiple comma-separated tags each autocomplete independently
- [ ] All 101 existing tests still pass
- [ ] New tests added (≥10) and passing
- [ ] Coverage ≥92% maintained
- [ ] Manual testing confirms smooth UX
- [ ] Code formatted (black) and linted (pylint)

---

## Documentation Updates

After implementation:
- Add section to `CLAUDE.md` under "Recent Features"
- Update `FuzzyTagCompleter` class docstring
- Update `SnippetManager.get_all_tags()` docstring
- Add usage notes in `snippet_editor_dialog.py`
- Consider adding to user-facing documentation (README.md)

---

## References

- **Project**: Quick Snippet Overlay v1.0
- **Architecture**: See `HANDOFF-ADVANCED-FEATURES.md`
- **Testing Standards**: See `CLAUDE.md` (92% coverage, TDD required)
- **Dependencies**: rapidfuzz 3.14.3, PySide6 6.10.0

---

**Status**: Not Started
**Created**: 2025-11-05
**Last Updated**: 2025-11-05
