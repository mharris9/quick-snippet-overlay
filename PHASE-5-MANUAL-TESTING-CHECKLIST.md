# Phase 5: Manual Testing Checklist

## Overview
This checklist guides manual testing of the tag autocomplete feature in the running application. Complete each scenario and check off when verified.

**Status:** Ready for manual testing

---

## Setup

- [ ] Virtual environment activated (`.\.venv\Scripts\Activate.ps1`)
- [ ] Application started (`python src/main.py`)
- [ ] System tray icon visible
- [ ] Snippet editor accessible

---

## Test Scenarios

### Basic Tag Autocomplete

**Scenario 1: Open Snippet Editor**
- [ ] Right-click system tray icon
- [ ] Click "Edit Snippets"
- [ ] Snippet editor dialog opens without errors
- [ ] Tags field is visible and accepts input

**Scenario 2: Single Tag Autocomplete**
- [ ] Type in tags field: "pyt"
- [ ] Dropdown appears with suggestions
- [ ] Suggestions include: "python" (fuzzy match)
- [ ] Select "python" from dropdown
- [ ] Field shows "python"

**Scenario 3: Typo Tolerance**
- [ ] Type in tags field: "pyton" (intentional typo)
- [ ] Dropdown shows "python" (fuzzy match)
- [ ] Score threshold filters weak matches

---

### Multi-Tag Autocomplete

**Scenario 4: Comma-Separated Tags**
- [ ] Type in tags field: "python, "
- [ ] Completer resets (ready for new tag)
- [ ] Type: "py"
- [ ] Dropdown shows suggestions for "py"
- [ ] Select "pyside"
- [ ] Field shows: "python, pyside"

**Scenario 5: Multiple Commas**
- [ ] Type: "python, pyside, test"
- [ ] Each tag gets independent suggestions
- [ ] Dropdown updates as you type after each comma

**Scenario 6: Whitespace Handling**
- [ ] Type: "python , pyside "
- [ ] Save snippet
- [ ] Tags saved as: ["python", "pyside"] (trimmed)

---

### Edge Cases

**Scenario 7: Empty Tags**
- [ ] Type: "python,,pyside"
- [ ] Save snippet
- [ ] Empty tag filtered out
- [ ] Tags: ["python", "pyside"]

**Scenario 8: Trailing Comma**
- [ ] Type: "python,"
- [ ] Completer ready for next tag
- [ ] Type: "p"
- [ ] Suggestions appear

**Scenario 9: No Existing Tags**
- [ ] Create new snippet with no tags
- [ ] Completer handles empty tag list gracefully
- [ ] No crash or errors

**Scenario 10: Case Insensitivity**
- [ ] Type: "PYTHON"
- [ ] Matches "python" (case insensitive)
- [ ] Type: "PySide"
- [ ] Matches "pyside"

---

### Regression Testing

**Existing Functionality:**
- [ ] Test overlay hotkey (Ctrl+Shift+Space)
- [ ] Test fuzzy search in overlay
- [ ] Test variable substitution
- [ ] Test snippet saving/loading
- [ ] Test system tray integration

---

## Notes

**Expected Behavior:**
- Dropdown appears within 50-100ms
- Fuzzy matching tolerates typos
- Comma-separated tags work independently
- Whitespace is automatically trimmed
- Empty tags are filtered out

**Known Issues:**
- None specific to tag autocomplete

**Observations:**
[Add notes here after testing]

---

## Sign-Off

- [ ] All scenarios tested
- [ ] All scenarios passed
- [ ] No regressions observed
- [ ] Feature is production-ready

**Tested By:** _________________
**Date:** _________________
**Notes:** _________________

---

Generated: 2025-11-05
