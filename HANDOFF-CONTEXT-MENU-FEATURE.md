# Phase: Context Menu for Snippet Right-Click

## Session Handoff Context

### Previous Session Accomplishments

**Frequency-Based Sorting Implementation ✅**
- Created `UsageTracker` class (`src/usage_tracker.py`) with YAML persistence
- Implemented sorting: frequency (descending) → alphabetical (ascending)
- Integrated with `OverlayWindow` for sorted display
- All 25 usage tracking tests passing (100%)
- Usage stats persist in `~/.quick-snippet-overlay/usage_stats.yaml`

**Bug Fixes ✅**
1. **Overlay Focus**: Fixed click-outside-to-close (now works immediately via `_activate_and_focus()`)
2. **Hotkey Toggle**: Fixed multiple overlay prevention (proper `isVisible()` check)
3. **Dialog Tracking**: Added `dialog_open` flag to prevent hotkey during editing
4. **Single Instance**: Implemented taskkill-based process enforcement

**Current Application State**
- ✅ App runs without errors
- ✅ Snippets display sorted by usage frequency
- ✅ Single instance enforcement working
- ✅ Dialog tracking prevents conflicts
- ✅ All core functionality tested and operational

### Codebase Structure (Relevant Files)

```
src/
├── main.py                      # Entry point, single-instance enforcement
├── overlay_window.py            # Main UI - TARGET FOR THIS PHASE
├── snippet_manager.py           # CRUD operations, sorting
├── usage_tracker.py             # Usage tracking (NEW - previous session)
├── delete_snippets_dialog.py   # Delete dialog (mass deletion)
├── snippet_editor_dialog.py    # Add/Edit dialog
└── variable_handler.py          # Variable substitution
```

**Key Overlay Window Methods:**
- `_on_edit_snippet_clicked()` - Opens edit dialog for selected snippet
- `_on_delete_snippets_clicked()` - Opens delete dialog (all snippets)
- `results_list` (QListWidget) - Contains snippet items

---

## Objective

Implement **right-click context menu** on snippets in the overlay window with two options:
1. **Edit** - Open edit dialog for the clicked snippet
2. **Delete** - Open delete dialog with only the clicked snippet selected

### Success Criteria

**Functional Requirements:**
- [ ] Right-clicking a snippet displays a context menu
- [ ] Context menu has "Edit" and "Delete" options
- [ ] "Edit" opens `SnippetEditorDialog` for that specific snippet
- [ ] "Delete" opens `DeleteSnippetsDialog` with only that snippet pre-selected
- [ ] Context menu respects `dialog_open` flag (no menu during editing)
- [ ] Right-click also selects the snippet (if not already selected)

**Technical Requirements:**
- [ ] No regressions in existing functionality
- [ ] All existing tests still pass
- [ ] Code follows PySide6 best practices
- [ ] Proper error handling
- [ ] Clean integration with existing methods

**Testing Requirements:**
- [ ] Manual testing of context menu interaction
- [ ] Verify edit flow works from context menu
- [ ] Verify delete flow works from context menu
- [ ] Verify context menu disabled during dialog editing
- [ ] Test with keyboard navigation (should still work)

---

## Parallelization Analysis

**Assessment: SEQUENTIAL IMPLEMENTATION ONLY**

**Reasoning:**
1. ❌ **Single File**: Only `src/overlay_window.py` requires changes
2. ❌ **No File Independence**: Context menu tightly coupled to existing overlay logic
3. ❌ **Shared State**: Interacts with `dialog_open` flag, `results_list`, selection state
4. ❌ **Integration Required**: Must connect to existing `_on_edit_snippet_clicked()` and `_on_delete_snippets_clicked()`

**Verdict**: No subagents needed. Direct implementation in main session.

---

## Implementation Plan

### Task 1: Add Context Menu to results_list

**Location:** `src/overlay_window.py` in `_setup_ui()` method

```python
# Enable context menu on results_list
self.results_list.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
```

### Task 2: Implement Context Menu Handler

**Location:** `src/overlay_window.py` - new method

```python
def _show_context_menu(self, position):
    """Show context menu on right-click."""
    # Get item at position
    item = self.results_list.itemAt(position)
    if not item:
        return

    # Don't show menu if dialog is open
    if self.dialog_open:
        return

    # Select the item (if not already selected)
    self.results_list.setCurrentItem(item)

    # Create menu
    menu = QMenu(self)
    edit_action = menu.addAction("Edit")
    delete_action = menu.addAction("Delete")

    # Connect actions
    edit_action.triggered.connect(self._on_edit_snippet_clicked)
    delete_action.triggered.connect(lambda: self._on_delete_single_snippet())

    # Show menu at cursor position
    menu.exec(self.results_list.mapToGlobal(position))
```

### Task 3: Connect Signal

**Location:** `src/overlay_window.py` in `_setup_connections()` method

```python
self.results_list.customContextMenuRequested.connect(self._show_context_menu)
```

### Task 4: Implement Single Snippet Delete

**Location:** `src/overlay_window.py` - new method

Create wrapper around existing delete dialog that pre-selects only the current snippet:

```python
def _on_delete_single_snippet(self):
    """Delete the currently selected snippet via context menu."""
    current_item = self.results_list.currentItem()
    if not current_item:
        return

    snippet = current_item.data(Qt.ItemDataRole.UserRole)
    if not snippet:
        return

    # Mark dialog as open
    self.dialog_open = True

    try:
        # Show confirmation
        from PySide6.QtWidgets import QMessageBox
        reply = QMessageBox.question(
            self,
            "Delete Snippet",
            f"Are you sure you want to delete '{snippet.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Delete the snippet
            self.snippet_manager.delete_snippets([snippet.id])

            # Reload and refresh
            self.reload_snippets()
            self._update_results(self.search_input.text())
    finally:
        self.dialog_open = False
```

### Task 5: Test Integration

**Manual Test Plan:**
1. Run app, open overlay
2. Right-click on a snippet → context menu appears
3. Click "Edit" → edit dialog opens with correct snippet
4. Make changes, save → snippet updates correctly
5. Right-click again, choose "Delete" → confirmation dialog appears
6. Confirm delete → snippet removed, overlay updates
7. Open edit dialog, then try right-click → no context menu (dialog_open flag working)

---

## Standard Coding Pattern

### 1. Context Review
- ✅ Read `src/overlay_window.py` (current implementation)
- ✅ Review existing edit/delete methods
- ✅ Understand `dialog_open` flag usage

### 2. Analysis
- Context menu adds new interaction pattern
- Must integrate cleanly with existing keyboard navigation
- Must respect dialog tracking to prevent conflicts
- No new dependencies required (PySide6 has QMenu built-in)

### 3. Constructive Critic Review
**Invoke constructive-critic subagent to evaluate:**
- Potential UX issues (e.g., menu conflicts with double-click)
- Error cases (e.g., item deleted while menu open)
- Accessibility concerns (keyboard-only users)
- Integration risks with existing dialog tracking

### 4. Implementation
1. Add context menu policy to `results_list`
2. Implement `_show_context_menu()` handler
3. Implement `_on_delete_single_snippet()` wrapper
4. Connect signal in `_setup_connections()`
5. Test manually

### 5. Verification
- [ ] App starts without errors
- [ ] Context menu appears on right-click
- [ ] Edit action works correctly
- [ ] Delete action works correctly
- [ ] No menu during dialog editing
- [ ] Keyboard navigation still functional

### 6. Documentation
Update `CLAUDE.md` or create `CONTEXT-MENU-FEATURE.md` with:
- Feature description
- Usage instructions
- Implementation notes

### 7. Delivery
- Commit changes with descriptive message
- Report to user with test results
- Note any edge cases or limitations

---

## Known Risks & Mitigation

### Risk 1: Menu Conflicts with Double-Click
**Mitigation:** Qt handles this automatically - right-click shows menu, double-click triggers selection

### Risk 2: Item Deleted While Menu Open
**Mitigation:** Menu closes when focus lost; subsequent action will fail gracefully with no item selected

### Risk 3: Keyboard-Only Users
**Mitigation:** Existing keyboard shortcuts (Ctrl+N for add) still work; context menu is convenience feature only

### Risk 4: Dialog Tracking Edge Cases
**Mitigation:** `dialog_open` flag already implemented; test thoroughly with manual testing

---

## Open Questions

None identified. Requirements are clear and implementation is straightforward.

---

## Dependencies

**No new dependencies required.**
- Uses built-in PySide6 QMenu
- Leverages existing dialog methods
- No package installation needed

---

## Meta

**Loop Policy:** Iterate until all manual tests pass
**Communication:** Report progress, blockers, and test results clearly
**Success Definition:** User can right-click → edit or delete → no regressions

---

## Estimated Effort

**Time Estimate:** 30-45 minutes
- Implementation: 15-20 minutes
- Manual testing: 10-15 minutes
- Documentation: 5-10 minutes

**Complexity:** Low (integrating existing components with standard PySide6 pattern)
