# Phase 5: Overlay Window UI Foundation - Todo List

## Progress Tracking
**Started**: 2025-11-04
**Status**: IN PROGRESS
**Current Step**: Not started

## 12-Step TDD Workflow

### Step 1: Review Phase 5 Requirements (15 min) - NOT STARTED
- [ ] Read PRD Section 9: User Experience (Lines 662-748)
- [ ] Read Implementation Plan Phase 5 (Lines 720-1044)
- [ ] Document understanding of overlay specifications
- [ ] Document understanding of search functionality
- [ ] Document understanding of keyboard navigation
- [ ] Document understanding of variable prompts
- [ ] Document understanding of multi-monitor support
**Expected Output**: Requirements summary documented

### Step 2: Install PyQt6 and pynput Dependencies (10 min) - NOT STARTED
- [ ] Install PyQt6 (pip install PyQt6)
- [ ] Install pynput (pip install pynput)
- [ ] Verify PyQt6.QtWidgets import
- [ ] Verify PyQt6.QtCore import
- [ ] Verify PyQt6.QtGui import
- [ ] Verify pynput.keyboard import
**Expected Output**: All imports successful

### Step 3: Create Test File Structure for overlay_window.py (15 min) - NOT STARTED
- [ ] Create tests/test_overlay_window.py
- [ ] Add app fixture (QApplication instance)
- [ ] Add overlay_window fixture
- [ ] Create test_window_creation stub
- [ ] Create test_window_positioning_active_monitor stub
- [ ] Create test_window_positioning_fallback_to_primary stub
- [ ] Create test_search_input_focus stub
- [ ] Create test_search_updates_results stub
- [ ] Create test_keyboard_navigation stub
- [ ] Create test_enter_key_with_no_variables_copies_directly stub
- [ ] Create test_enter_key_with_variables_shows_prompt stub
- [ ] Create test_escape_key_closes_window stub
- [ ] Create test_truncation_display stub
- [ ] Create test_empty_search_state stub
- [ ] Create test_copied_visual_feedback_appears stub
**Expected Output**: 13 test stubs created

### Step 4: Create Test File Structure for variable_prompt_dialog.py (15 min) - NOT STARTED
- [ ] Create tests/test_variable_prompt_dialog.py
- [ ] Add app fixture
- [ ] Create test_dialog_shows_variable_name stub
- [ ] Create test_dialog_prepopulates_default_value stub
- [ ] Create test_dialog_ok_button_returns_value stub
- [ ] Create test_dialog_cancel_button_returns_none stub
- [ ] Create test_dialog_empty_input_shows_error stub
- [ ] Create test_sequential_prompts_for_multiple_variables stub
- [ ] Create test_cancel_during_sequential_prompts_aborts stub
**Expected Output**: 7 test stubs created

### Step 5: Write Variable Prompt Dialog Tests (30 min) - NOT STARTED
- [ ] Implement test_dialog_shows_variable_name with assertions
- [ ] Implement test_dialog_prepopulates_default_value with assertions
- [ ] Implement test_dialog_ok_button_returns_value with assertions
- [ ] Implement test_dialog_cancel_button_returns_none with assertions
- [ ] Implement test_dialog_empty_input_shows_error with assertions
- [ ] Implement test_sequential_prompts_for_multiple_variables with assertions
- [ ] Implement test_cancel_during_sequential_prompts_aborts with assertions
- [ ] Run: python -m pytest tests/test_variable_prompt_dialog.py -v
**Expected Output**: All 7 tests FAIL (red phase)

### Step 6: Implement Variable Prompt Dialog (45 min) - NOT STARTED
- [ ] Create src/variable_prompt_dialog.py
- [ ] Implement VariablePromptDialog class
- [ ] Add __init__ with variable_name and default_value params
- [ ] Add _setup_ui method (label, input, buttons)
- [ ] Add _on_ok method with validation
- [ ] Add get_value method
- [ ] Implement prompt_for_variables helper function
- [ ] Run: python -m pytest tests/test_variable_prompt_dialog.py -v
**Expected Output**: 7/7 tests PASS (95%+ pass rate)

### Step 7: Write Overlay Window Tests (45 min) - NOT STARTED
- [ ] Implement test_window_creation with assertions
- [ ] Implement test_window_positioning_active_monitor with assertions
- [ ] Implement test_window_positioning_fallback_to_primary with assertions
- [ ] Implement test_search_input_focus with assertions
- [ ] Implement test_search_updates_results with assertions
- [ ] Implement test_keyboard_navigation with assertions
- [ ] Implement test_enter_key_with_no_variables_copies_directly with assertions
- [ ] Implement test_enter_key_with_variables_shows_prompt with assertions
- [ ] Implement test_escape_key_closes_window with assertions
- [ ] Implement test_truncation_display with assertions
- [ ] Implement test_empty_search_state with assertions
- [ ] Implement test_copied_visual_feedback_appears with assertions
- [ ] Run: python -m pytest tests/test_overlay_window.py -v
**Expected Output**: All 13 tests FAIL (red phase)

### Step 8: Implement Overlay Window - Part 1 (45 min) - NOT STARTED
- [ ] Create src/overlay_window.py
- [ ] Implement OverlayWindow class skeleton
- [ ] Add __init__ with all component dependencies
- [ ] Implement _setup_ui method (window flags, size, opacity)
- [ ] Add search_input widget
- [ ] Add results_list widget
- [ ] Add copied_label widget
- [ ] Implement show_overlay method with multi-monitor support
- [ ] Implement hide_overlay method
- [ ] Run tests 1-4
**Expected Output**: Tests 1-4 PASS

### Step 9: Implement Overlay Window - Part 2 (45 min) - NOT STARTED
- [ ] Add _setup_connections method
- [ ] Implement _on_search_input_changed with debounce timer
- [ ] Implement _update_results method
- [ ] Add truncation logic (2 lines max)
- [ ] Implement keyPressEvent (Enter, ESC, arrows)
- [ ] Implement _on_snippet_selected method
- [ ] Implement _copy_snippet_to_clipboard method
- [ ] Add variable prompt integration
- [ ] Implement _show_copied_feedback method
- [ ] Run: python -m pytest tests/test_overlay_window.py -v
**Expected Output**: 13/13 tests PASS (95%+ pass rate)

### Step 10: Verify Coverage (15 min) - NOT STARTED
- [ ] Run coverage for overlay_window.py
- [ ] Run coverage for variable_prompt_dialog.py
- [ ] Check coverage percentage (target ≥90%)
- [ ] Add tests for uncovered lines if needed
**Expected Output**: ≥90% coverage for both files

### Step 11: Manual UI Testing (30 min) - NOT STARTED
- [ ] Create manual test script
- [ ] Test overlay appearance (frameless, always-on-top, centered)
- [ ] Test multi-monitor centering
- [ ] Test search with debouncing
- [ ] Test keyboard navigation (arrows, Enter, ESC)
- [ ] Test variable prompts (single and multiple)
- [ ] Test Cancel during prompts
- [ ] Test "Copied!" visual feedback
- [ ] Document results
**Expected Output**: Manual test results documented

### Step 12: Create Phase 5 Completion Report (20 min) - NOT STARTED
- [ ] Create PHASE-5-COMPLETION-REPORT.md
- [ ] Write Executive Summary
- [ ] Write Implementation Details
- [ ] Write Test Results section
- [ ] Write Edge Cases Handled section
- [ ] Write UI/UX Notes section
- [ ] Write Integration Points section
- [ ] Write Manual Testing Results section
- [ ] Write Lessons Learned section
- [ ] Write Next Steps section
**Expected Output**: Completion report created

## Success Criteria
- [ ] 20/20 tests passing (95%+ pass rate)
- [ ] ≥90% coverage for overlay_window.py
- [ ] ≥90% coverage for variable_prompt_dialog.py
- [ ] All Phase 1-4 tests still passing (58/58)
- [ ] Manual testing complete
- [ ] Completion report finalized

## Time Tracking
- Estimated: 4.5-5.5 hours
- Actual: TBD
- Started: 2025-11-04
- Completed: TBD
