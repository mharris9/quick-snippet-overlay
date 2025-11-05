# Manual Testing Execution - Session Tracker

**Date Started**: 2025-11-04
**Tester**: _________________
**Session Goal**: Complete all 20 manual test cases
**Estimated Time**: 45-60 minutes

---

## Quick Start

### Step 1: Launch Application

Open PowerShell in project directory:

```powershell
cd C:\Users\mikeh\software_projects\quick-snippet-overlay
.\RUN-APP.ps1
```

**Expected**: Console shows "Launching Quick Snippet Overlay..." and system tray icon appears.

**Actual**: ☐ Success  ☐ Failed (note error below)

**Notes**: _______________________________________________________________

---

## Testing Workflow

### Phase 1: Core Features (Tests 1-4)

#### Test 1: Application Startup
**Time**: 2 minutes

**Steps**:
1. Application launched via RUN-APP.ps1
2. Check console for errors
3. Look for system tray icon (bottom-right taskbar)

**Results**:
- ☐ No errors in console
- ☐ System tray icon visible
- ☐ Application ready

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 2: System Tray Icon
**Time**: 2 minutes

**Steps**:
1. Right-click system tray icon
2. Verify menu items appear:
   - Open Overlay (Ctrl+Shift+Space)
   - Edit Snippets
   - Reload Snippets
   - Settings
   - About
   - Exit

**Results**:
- ☐ Menu appears on right-click
- ☐ All menu items present
- ☐ Menu items readable

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 3: Open Overlay via Menu
**Time**: 2 minutes

**Steps**:
1. Right-click tray icon
2. Click "Open Overlay (Ctrl+Shift+Space)"
3. Observe overlay window

**Results**:
- ☐ Overlay window appears
- ☐ Window centered on screen
- ☐ Search box visible and focused
- ☐ Snippet list visible below search box

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 4: Global Hotkey Activation
**Time**: 3 minutes

**Steps**:
1. Close overlay (Esc key)
2. Open Notepad or any application
3. Press **Ctrl+Shift+Space**
4. Observe overlay appears
5. Try from 2-3 different applications

**Results**:
- ☐ Hotkey works from Notepad
- ☐ Hotkey works from: ________________
- ☐ Hotkey works from: ________________
- ☐ Overlay appears on top of all windows

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 2: Search Features (Tests 5-7)

#### Test 5: Fuzzy Search
**Time**: 5 minutes

**Steps**:
1. Open overlay (Ctrl+Shift+Space)
2. Test these search queries:

| Query | Expected Result | Found? | Top Match |
|-------|-----------------|--------|-----------|
| git | Git snippets | ☐ | _________________ |
| python | Python snippets | ☐ | _________________ |
| powershell | PowerShell snippets | ☐ | _________________ |
| gti | Still finds git (typo) | ☐ | _________________ |
| network | Network snippets | ☐ | _________________ |

**Results**:
- ☐ All searches return results
- ☐ Results update as you type
- ☐ Typo tolerance works (gti → git)
- ☐ Results appear instant (<50ms feel)

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 6: Snippet Selection and Copying
**Time**: 5 minutes

**Steps**:
1. Open overlay
2. Search for "python"
3. Select "Install Python requirements"
4. Press Enter
5. Overlay should close
6. Open Notepad
7. Press Ctrl+V

**Expected Content**: `pip install -r requirements.txt`

**Actual Content**: _______________________________________________________________

**Results**:
- ☐ Snippet copied to clipboard
- ☐ Overlay closed after selection
- ☐ Content matches expected
- ☐ No extra whitespace or formatting issues

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 7: Keyboard Navigation
**Time**: 3 minutes

**Steps**:
1. Open overlay
2. Type "git"
3. Use ↓ arrow key to move down list
4. Use ↑ arrow key to move up list
5. Press Enter on selected item

**Results**:
- ☐ Down arrow selects next item
- ☐ Up arrow selects previous item
- ☐ Selected item highlighted
- ☐ Enter copies selected item

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 3: Variable Features (Tests 8-9)

#### Test 8: Variable Detection and Prompting
**Time**: 5 minutes

**Steps**:
1. Open overlay
2. Search for "Find file by name pattern" (has `{{pattern:*.txt}}`)
3. Press Enter
4. Variable prompt dialog should appear

**Results**:
- ☐ Dialog shows variable name: "pattern"
- ☐ Default value shown: "*.txt"
- ☐ Can edit the value
- ☐ OK button works
- ☐ Cancel button works

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 9: Variable Substitution
**Time**: 5 minutes

**Steps**:
1. Open overlay
2. Search for "Find process using a port" (has `{{port:8080}}`)
3. Press Enter
4. In prompt dialog, change "8080" to "3000"
5. Click OK
6. Paste in Notepad

**Expected**: `netstat -ano | findstr :3000`

**Actual**: _______________________________________________________________

**Results**:
- ☐ Variable substituted correctly
- ☐ Custom value used (not default)
- ☐ No {{}} braces in final output

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 4: File Operations (Tests 10-11)

#### Test 10: Edit Snippets
**Time**: 3 minutes

**Steps**:
1. Right-click tray icon
2. Click "Edit Snippets"
3. Observe file opens in editor

**Results**:
- ☐ snippets.yaml opens in default editor
- ☐ File path: C:\Users\mikeh\snippets\snippets.yaml
- ☐ File is editable

**Editor Used**: _______________________________________________________________

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 11: Hot-Reload Snippets
**Time**: 5 minutes

**Steps**:
1. Keep application running
2. Edit snippets.yaml in text editor
3. Add new snippet:
   ```yaml
   - id: test-reload-snippet
     name: TEST HOT RELOAD
     description: Test snippet for hot reload
     content: This snippet was added during testing
     tags: [test]
     created: 2025-11-04
     modified: 2025-11-04
   ```
4. Save file
5. Wait 2-3 seconds
6. Open overlay
7. Search for "TEST HOT RELOAD"

**Results**:
- ☐ New snippet appears without restart
- ☐ Search finds the new snippet
- ☐ Can copy the new snippet
- ☐ Console shows "Reloaded snippets" or similar

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 5: System Features (Tests 12-14)

#### Test 12: About Dialog
**Time**: 2 minutes

**Steps**:
1. Right-click tray icon
2. Click "About"

**Results**:
- ☐ Dialog appears
- ☐ Shows application name
- ☐ Shows version info
- ☐ Dialog can be closed

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 13: Single Instance Enforcement
**Time**: 3 minutes

**Steps**:
1. Application already running
2. Open NEW PowerShell window
3. Navigate to project directory
4. Run: `.\RUN-APP.ps1`

**Results**:
- ☐ Error message appears
- ☐ Message says "already running" or similar
- ☐ Second instance doesn't start
- ☐ First instance still running normally

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 14: Escape Key Closes Overlay
**Time**: 1 minute

**Steps**:
1. Open overlay (Ctrl+Shift+Space)
2. Press Esc key

**Results**:
- ☐ Overlay closes immediately
- ☐ Application still running (tray icon visible)

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 6: Error Scenarios (Tests 15-17)

#### Test 15: Corrupted YAML Handling
**Time**: 5 minutes

**Steps**:
1. Open snippets.yaml in editor
2. Introduce syntax error (remove a closing quote)
3. Save file
4. Right-click tray → "Reload Snippets"

**Results**:
- ☐ Error message appears (not crash)
- ☐ Message is helpful/clear
- ☐ Application still running
- ☐ Old snippets still available
- ☐ Fix error, reload works

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 16: Empty Search
**Time**: 1 minute

**Steps**:
1. Open overlay
2. Don't type anything (empty search)
3. Observe snippet list

**Results**:
- ☐ Shows all snippets OR shows nothing
- ☐ No crash or error
- ☐ Behavior is consistent

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 17: No Results Search
**Time**: 1 minute

**Steps**:
1. Open overlay
2. Type: "zzzzzzzzzz" (gibberish)

**Results**:
- ☐ No results shown (empty list)
- ☐ No crash or error
- ☐ Can still type and search again

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 7: Performance (Tests 18-19)

#### Test 18: Startup Time
**Time**: 3 minutes

**Steps**:
1. Exit application (right-click tray → Exit)
2. Use stopwatch or note time
3. Run: `.\RUN-APP.ps1`
4. Time until tray icon appears

**Measured Time**: __________ seconds

**Results**:
- ☐ Startup < 2 seconds (EXCELLENT)
- ☐ Startup 2-5 seconds (GOOD)
- ☐ Startup > 5 seconds (SLOW)

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

#### Test 19: Search Responsiveness
**Time**: 2 minutes

**Steps**:
1. Open overlay
2. Type rapidly: "gitpythonpowershellnetwork"
3. Observe if search keeps up

**Results**:
- ☐ Search feels instant
- ☐ No lag while typing
- ☐ Results update smoothly

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

### Phase 8: Edge Cases (Test 20)

#### Test 20: Multi-Monitor (if applicable)
**Time**: 2 minutes

**Skip if you don't have multiple monitors**: ☐

**Steps**:
1. If you have 2+ monitors
2. Click on secondary monitor
3. Press Ctrl+Shift+Space

**Results**:
- ☐ Overlay appears on active/primary monitor
- ☐ Overlay is accessible

**Status**: ☐ PASS  ☐ FAIL  ☐ SKIPPED

**Issues**: _______________________________________________________________

---

### Final Test: Graceful Exit

#### Test 21: Application Exit
**Time**: 2 minutes

**Steps**:
1. Right-click tray icon
2. Click "Exit"
3. Check tray icon disappears
4. Check console (if still open)

**Results**:
- ☐ Tray icon disappears
- ☐ Application exits cleanly
- ☐ No error messages
- ☐ Lock file removed (check: C:\Users\mikeh\AppData\Local\QuickSnippetOverlay\app.lock)

**Status**: ☐ PASS  ☐ FAIL

**Issues**: _______________________________________________________________

---

## Test Summary

### Results Overview

**Fill out after completing all tests**:

| Category | Tests | Passed | Failed |
|----------|-------|--------|--------|
| Core Features (1-4) | 4 | ____ | ____ |
| Search Features (5-7) | 3 | ____ | ____ |
| Variable Features (8-9) | 2 | ____ | ____ |
| File Operations (10-11) | 2 | ____ | ____ |
| System Features (12-14) | 3 | ____ | ____ |
| Error Scenarios (15-17) | 3 | ____ | ____ |
| Performance (18-19) | 2 | ____ | ____ |
| Edge Cases (20) | 1 | ____ | ____ |
| Final (21) | 1 | ____ | ____ |
| **TOTAL** | **21** | **____** | **____** |

### Critical Issues Found (P0 - Blocks Release)

**List any critical issues that prevent the application from working**:

1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

### High Priority Issues (P1 - Should Fix)

**List important issues that impact functionality**:

1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

### Minor Issues (P2 - Nice to Fix)

**List cosmetic or minor issues**:

1. _______________________________________________________________
2. _______________________________________________________________
3. _______________________________________________________________

### Observations & Notes

**General feedback, usability notes, or suggestions**:

_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
_______________________________________________________________

---

## Decision

Based on test results:

☐ **PROCEED TO PHASE 7**: All critical tests passed, ready for packaging

☐ **FIX ISSUES FIRST**: Critical issues found, need fixes before Phase 7

☐ **MORE TESTING NEEDED**: Uncertain, need additional validation

---

## Next Steps

### If PROCEED TO PHASE 7:
1. Document test completion
2. Create Phase 7 handoff document
3. Begin packaging (PyInstaller, Inno Setup)

### If FIX ISSUES FIRST:
1. Document all issues clearly
2. Prioritize fixes (P0 → P1 → P2)
3. Fix critical issues
4. Re-run failed tests
5. Then proceed to Phase 7

---

**Testing Completed**: ☐ Yes  ☐ No

**Date Completed**: __________________

**Total Time Spent**: __________ minutes

**Tester Signature**: __________________

---

## How to Report Results

After completing testing, create a simple report:

```
MANUAL TESTING RESULTS - 2025-11-04

Tests Passed: ____ / 21
Tests Failed: ____ / 21

Critical Issues: ____
High Priority Issues: ____
Minor Issues: ____

Decision: PROCEED TO PHASE 7 / FIX ISSUES FIRST

[Brief summary of findings]
```

Then share with development team (or proceed to Phase 7 if ready).
