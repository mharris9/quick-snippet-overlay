# Phase: Frequency-Based Snippet Sorting

## Objective
Implement usage tracking and frequency-based sorting for snippets in the overlay window. Snippets should be sorted by copy frequency (most frequently copied first), with alphabetical sorting as a secondary tiebreaker for snippets with equal usage counts.

## Current State
- Backup and restore system fully implemented and tested (100% tests passing)
- Snippets currently display in order loaded from YAML file
- No usage tracking exists
- All tests passing for existing features

## Requirements

### 1. Usage Tracking System
- Track how many times each snippet is copied to clipboard
- Persist usage counts across app restarts
- Store usage data in separate file (e.g., `usage_stats.json` or `usage_stats.yaml`)
- Usage data schema:
  ```yaml
  snippet_usage:
    snippet-id-1: 42
    snippet-id-2: 15
    snippet-id-3: 8
  ```

### 2. Sorting Logic
- **Primary sort**: Copy frequency (descending - most used first)
- **Secondary sort**: Alphabetical by name (ascending - A to Z)
- **Behavior for new snippets**: Snippets with 0 usage appear at bottom, sorted alphabetically
- **Behavior for deleted snippets**: Clean up orphaned usage stats when snippets deleted

### 3. Integration Points
- Increment usage count when snippet copied to clipboard (in `variable_handler.py` or wherever clipboard copy happens)
- Load usage stats on app startup
- Save usage stats after each copy (or debounced save)
- Apply sorting in `overlay_window.py` search results display
- Apply sorting in fuzzy search results from `search_engine.py`

### 4. User Control (Optional Enhancement)
- Consider adding menu option to reset usage statistics
- Consider adding menu option to toggle sorting mode (frequency vs alphabetical)

## Success Criteria
- ✅ All existing tests continue passing (100%)
- ✅ New tests written and passing for:
  - Usage tracking increment
  - Usage stats persistence (load/save)
  - Sorting algorithm (frequency + alphabetical)
  - Orphaned stats cleanup
- ✅ Test coverage maintained at ≥85% per component
- ✅ Snippets display in correct frequency order in overlay
- ✅ Usage counts persist across app restarts
- ✅ Performance: Sorting adds <50ms latency to search results

## Implementation Approach

### TDD - Tests First
1. Write tests for `UsageTracker` class (or similar):
   - `test_increment_usage_count()`
   - `test_load_usage_stats_from_file()`
   - `test_save_usage_stats_to_file()`
   - `test_get_usage_count_for_snippet()`
   - `test_cleanup_orphaned_stats()`

2. Write tests for sorting:
   - `test_sort_snippets_by_frequency_descending()`
   - `test_sort_snippets_alphabetically_when_frequency_tied()`
   - `test_new_snippets_appear_at_bottom()`

3. Write integration tests:
   - `test_usage_increments_on_copy()`
   - `test_overlay_displays_sorted_results()`

### Code Implementation
1. Create `src/usage_tracker.py` with:
   - `UsageTracker` class
   - `increment(snippet_id)` method
   - `get_count(snippet_id)` method
   - `load()` and `save()` methods
   - `cleanup_orphaned(valid_snippet_ids)` method

2. Update `src/snippet_manager.py`:
   - Add method to get sorted snippets list
   - Integrate with `UsageTracker`

3. Update clipboard copy location (find where `pyperclip.copy()` is called):
   - Inject `UsageTracker.increment(snippet_id)` call

4. Update `src/overlay_window.py`:
   - Sort search results using new sorting logic

5. Update `src/search_engine.py` (if sorting happens here):
   - Apply frequency-based sorting to search results

## Files to Create/Modify
- **NEW**: `src/usage_tracker.py` - Usage tracking class
- **NEW**: `tests/test_usage_tracker.py` - Usage tracker tests
- **MODIFY**: `src/snippet_manager.py` - Add sorted snippets method
- **MODIFY**: `src/overlay_window.py` - Apply sorting to display
- **MODIFY**: `src/variable_handler.py` or wherever clipboard copy occurs - Increment usage
- **MODIFY**: `tests/test_snippet_manager.py` - Add sorting tests
- **MODIFY**: `tests/test_overlay_window.py` - Add display sorting tests

## Testing Strategy
1. Unit tests for `UsageTracker` class (load, save, increment, cleanup)
2. Unit tests for sorting algorithm
3. Integration tests for usage increment on copy
4. Integration tests for overlay display order
5. Edge case tests:
   - Empty usage stats file
   - Corrupted usage stats file (fallback to defaults)
   - Snippet deleted but still in usage stats
   - All snippets have 0 usage (alphabetical order)
   - All snippets have same usage count (alphabetical tiebreaker)

## Performance Considerations
- Usage stats save should be debounced (don't write to disk on every copy)
- Sorting should happen once per search, not per result
- Usage stats file should be small (just snippet IDs and counts)

## Backward Compatibility
- App should work fine if `usage_stats.yaml` doesn't exist (all counts = 0)
- Existing snippets.yaml format unchanged
- Existing backup/restore system unchanged

## Deliverables
1. All tests passing (100%)
2. Usage tracking implemented and tested
3. Frequency-based sorting implemented and tested
4. Usage stats persist across restarts
5. Clean code with docstrings
6. No regressions in existing functionality

## Next Steps After Completion
- Consider adding usage statistics visualization
- Consider adding "most used snippets" report
- Consider adding usage reset/clear feature in system tray menu

---

## Development Constraints
- Use TDD approach (tests before implementation)
- Maintain 100% test pass rate
- Follow existing code style and patterns
- Use PySide6 for any UI changes
- Store usage stats in YAML format (consistent with snippets.yaml)
- Create automatic backup before modifying usage stats file
