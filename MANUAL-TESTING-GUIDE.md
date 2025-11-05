# Manual Integration Testing Guide - Phase 6

**Application**: Quick Snippet Overlay
**Version**: Phase 6 Complete (Pre-v1.0)
**Test Date**: 2025-11-04
**Tester**: ___________
**Duration**: 30-60 minutes

---

## Prerequisites

### 1. Environment Setup

Ensure the following are ready:

```powershell
# Navigate to project directory
cd C:\Users\mikeh\software_projects\quick-snippet-overlay

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Verify all dependencies installed
pip list | Select-String "PySide6|pynput|pyperclip|watchdog|rapidfuzz|PyYAML"
```

Expected output:
- PySide6 (6.x)
- pynput (1.8.1)
- pyperclip (1.11.0)
- watchdog (6.0.0)
- rapidfuzz (3.x)
- PyYAML (6.x)

### 2. Configuration Files

Verify these files exist:
- `C:\Users\mikeh\snippets\snippets.yaml`
- `C:\Users\mikeh\snippets\config.yaml`

If missing, the application should create defaults on first run.

---

## Test Suite

### Test 1: Application Startup

**Objective**: Verify application starts without errors

**Steps**:
1. Open PowerShell in project directory
2. Activate venv: `.\.venv\Scripts\Activate.ps1`
3. Run: `python src/main.py`

**Expected Results**:
- [ ] No error messages in console
- [ ] System tray icon appears in Windows taskbar notification area
- [ ] No overlay window visible (should start hidden)
- [ ] Console shows initialization messages

**Pass/Fail**: ___________

**Notes**:
```
____________________________________________________________
____________________________________________________________
```

---

### Test 2: System Tray Icon

**Objective**: Verify system tray integration works

**Steps**:
1. Locate system tray icon (taskbar notification area)
2. Right-click the icon
3. Verify context menu appears

**Expected Results**:
- [ ] Icon is visible in system tray
- [ ] Right-click shows menu with items:
  - "Open Overlay (Ctrl+Shift+Space)"
  - "Edit Snippets"
  - "Reload Snippets"
  - "Settings" (may be disabled)
  - "About"
  - "Exit"

**Pass/Fail**: ___________

**Notes**:
```
____________________________________________________________
```

---

### Test 3: Open Overlay via Menu

**Objective**: Verify overlay can be opened from system tray menu

**Steps**:
1. Right-click system tray icon
2. Click "Open Overlay (Ctrl+Shift+Space)"

**Expected Results**:
- [ ] Overlay window appears
- [ ] Window is centered on screen
- [ ] Search box is focused and ready for input
- [ ] Window is frameless/transparent background
- [ ] Snippet list shows all available snippets

**Pass/Fail**: ___________

**Notes**:
```
____________________________________________________________
```

---

### Test 4: Global Hotkey Activation

**Objective**: Verify Ctrl+Shift+Space hotkey works system-wide

**Steps**:
1. Close overlay window (if open)
2. Open Notepad or any other application
3. Press **Ctrl+Shift+Space**

**Expected Results**:
- [ ] Overlay window appears
- [ ] Window appears on top of all other windows
- [ ] Search box is focused
- [ ] Works from any application (test in 2-3 different apps)

**Pass/Fail**: ___________

**Applications Tested**:
```
1. _____________________ (Pass/Fail: ____)
2. _____________________ (Pass/Fail: ____)
3. _____________________ (Pass/Fail: ____)
```

---

### Test 5: Fuzzy Search

**Objective**: Verify search engine finds snippets with typo tolerance

**Steps**:
1. Open overlay (Ctrl+Shift+Space)
2. Type various search terms:
   - Exact match: type snippet name exactly
   - Partial match: type first few letters
   - Typo: type with intentional typo (e.g., "gti" instead of "git")
   - Tag search: type a tag name
   - Content search: type words from snippet content

**Expected Results**:
- [ ] Exact matches appear at top
- [ ] Partial matches appear
- [ ] Typos still find correct snippets (fuzzy matching)
- [ ] Search is fast (<50ms feels instant)
- [ ] Results update as you type

**Search Tests**:
| Query | Expected Snippet | Found? (Y/N) | Position |
|-------|------------------|--------------|----------|
| _____ | _______________ | ____         | ____     |
| _____ | _______________ | ____         | ____     |
| _____ | _______________ | ____         | ____     |

**Pass/Fail**: ___________

---

### Test 6: Snippet Selection and Copying

**Objective**: Verify snippets copy to clipboard correctly

**Steps**:
1. Open overlay
2. Search for a simple snippet (no variables)
3. Press Enter or click to select
4. Open Notepad
5. Press Ctrl+V to paste

**Expected Results**:
- [ ] Snippet copied to clipboard
- [ ] Overlay closes after selection
- [ ] Pasted content matches snippet exactly
- [ ] No extra whitespace or formatting issues

**Pass/Fail**: ___________

**Snippet Tested**: ___________________

**Pasted Content**:
```
____________________________________________________________
____________________________________________________________
```

---

### Test 7: Variable Substitution

**Objective**: Verify variable prompts and substitution work

**Steps**:
1. Create/find snippet with variable syntax: `{{variable:default}}`
2. Open overlay and select the snippet
3. Fill in variable prompt dialog
4. Paste result in Notepad

**Expected Results**:
- [ ] Dialog prompts for variable value
- [ ] Default value pre-filled in dialog
- [ ] Can override default value
- [ ] Variable replaced in final snippet
- [ ] Multiple variables handled correctly

**Test Cases**:

**Case 1**: Variable with default
- Snippet: `Hello {{name:World}}`
- Variable entered: (use default)
- Expected result: `Hello World`
- Actual result: ___________________
- Pass/Fail: ___________

**Case 2**: Variable without default
- Snippet: `Hello {{name}}`
- Variable entered: `Mike`
- Expected result: `Hello Mike`
- Actual result: ___________________
- Pass/Fail: ___________

**Case 3**: Multiple variables
- Snippet: `{{greeting:Hi}} {{name}}, welcome to {{place:Earth}}`
- Variables entered: greeting=Hello, name=Alice, place=(default)
- Expected result: `Hello Alice, welcome to Earth`
- Actual result: ___________________
- Pass/Fail: ___________

---

### Test 8: Edit Snippets

**Objective**: Verify "Edit Snippets" menu action works

**Steps**:
1. Right-click system tray icon
2. Click "Edit Snippets"

**Expected Results**:
- [ ] Default editor opens snippets.yaml file
- [ ] File location: `C:\Users\mikeh\snippets\snippets.yaml`
- [ ] File is editable

**Pass/Fail**: ___________

**Notes**:
```
____________________________________________________________
```

---

### Test 9: Hot-Reload Snippets

**Objective**: Verify file watching and auto-reload works

**Steps**:
1. Open overlay and note current snippets
2. Keep application running
3. Edit `snippets.yaml` in text editor
4. Add a new snippet:
   ```yaml
   - name: "TEST-RELOAD"
     content: "This is a test of hot-reload"
     tags: ["test"]
   ```
5. Save file
6. Wait 2-3 seconds
7. Open overlay again and search for "TEST-RELOAD"

**Expected Results**:
- [ ] New snippet appears without restarting application
- [ ] Console shows reload message
- [ ] Search finds new snippet immediately

**Pass/Fail**: ___________

**Alternative Test - Manual Reload**:
1. Edit snippets.yaml
2. Right-click system tray → "Reload Snippets"
3. Verify changes applied

**Pass/Fail**: ___________

---

### Test 10: About Dialog

**Objective**: Verify "About" menu displays version info

**Steps**:
1. Right-click system tray icon
2. Click "About"

**Expected Results**:
- [ ] Dialog appears with application information
- [ ] Shows version number
- [ ] Shows description

**Pass/Fail**: ___________

---

### Test 11: Single Instance Enforcement

**Objective**: Verify only one instance can run

**Steps**:
1. Application already running
2. Open NEW PowerShell window
3. Navigate to project directory
4. Activate venv
5. Run: `python src/main.py` (second time)

**Expected Results**:
- [ ] Error dialog appears: "Quick Snippet Overlay is already running"
- [ ] Second instance exits
- [ ] First instance continues running normally
- [ ] Lock file exists: `C:\Users\mikeh\AppData\Local\QuickSnippetOverlay\app.lock`

**Pass/Fail**: ___________

---

### Test 12: Graceful Exit

**Objective**: Verify application shuts down cleanly

**Steps**:
1. Right-click system tray icon
2. Click "Exit"

**Expected Results**:
- [ ] System tray icon disappears
- [ ] Overlay window closes
- [ ] Application process terminates
- [ ] Lock file removed: `C:\Users\mikeh\AppData\Local\QuickSnippetOverlay\app.lock`
- [ ] No error messages in console

**Pass/Fail**: ___________

---

## Error Scenario Tests

### Error 1: Corrupted YAML File

**Steps**:
1. Backup `snippets.yaml`
2. Edit file and introduce syntax error (e.g., remove closing quote)
3. Save file
4. Wait for hot-reload OR click "Reload Snippets"

**Expected Results**:
- [ ] Error dialog displays with helpful message
- [ ] Application continues running
- [ ] Previous snippets still available
- [ ] Fix file and reload works

**Pass/Fail**: ___________

---

### Error 2: Missing Snippets File

**Steps**:
1. Exit application
2. Rename or move `C:\Users\mikeh\snippets\snippets.yaml`
3. Start application

**Expected Results**:
- [ ] Application starts successfully
- [ ] Creates default snippets.yaml file
- [ ] Default snippets available

**Pass/Fail**: ___________

---

### Error 3: Hotkey Already in Use

**Steps**:
1. Exit application
2. Edit `config.yaml` to use common hotkey (e.g., Ctrl+C)
3. Start application

**Expected Results**:
- [ ] Application starts (may show warning)
- [ ] Hotkey may not work due to conflict
- [ ] Application doesn't crash

**Pass/Fail**: ___________

**Notes**:
```
____________________________________________________________
```

---

## Performance Tests

### Performance 1: Startup Time

**Steps**:
1. Exit application
2. Measure time from running `python src/main.py` to tray icon appearing
3. Use stopwatch or note timestamps

**Expected Results**:
- [ ] Startup time < 2 seconds (cold start)
- [ ] Startup time < 1 second (warm start)

**Measured Time**: __________ seconds

**Pass/Fail**: ___________

---

### Performance 2: Search Latency

**Steps**:
1. Open overlay
2. Type search query
3. Observe results update speed

**Expected Results**:
- [ ] Results appear instantly (<50ms feels immediate)
- [ ] No lag or stuttering while typing
- [ ] Smooth scrolling in results list

**Pass/Fail**: ___________

---

### Performance 3: Memory Usage

**Steps**:
1. Application running in idle state
2. Open Task Manager
3. Find Python process
4. Note memory usage

**Expected Results**:
- [ ] Memory usage < 100MB (idle)
- [ ] No memory leaks (stays stable over time)

**Measured Memory**: __________ MB

**Pass/Fail**: ___________

---

## Multi-Monitor Tests (if applicable)

### Multi-Monitor 1: Overlay Positioning

**Steps**:
1. Connect second monitor
2. Open overlay
3. Note which monitor it appears on

**Expected Results**:
- [ ] Overlay appears on active/primary monitor
- [ ] Centered correctly on that monitor

**Pass/Fail**: ___________

---

## Edge Cases

### Edge 1: Windows Scaling (if not 100%)

**Steps**:
1. Check Windows display scaling (Settings → Display)
2. Open overlay
3. Verify text and controls are readable

**Scaling Setting**: ___________%

**Expected Results**:
- [ ] Overlay scales correctly
- [ ] Text readable (not blurry or too small)

**Pass/Fail**: ___________

---

### Edge 2: Special Characters in Snippets

**Steps**:
1. Create snippet with special characters: `& < > " ' \n \t {{  }}`
2. Select snippet
3. Paste in Notepad

**Expected Results**:
- [ ] Special characters preserved correctly
- [ ] No escaping issues

**Pass/Fail**: ___________

---

## Test Summary

### Overall Results

| Test Category | Tests Passed | Tests Failed | Pass Rate |
|---------------|--------------|--------------|-----------|
| Core Features | ____ / 12    | ____         | ____%     |
| Error Handling | ____ / 3    | ____         | ____%     |
| Performance   | ____ / 3     | ____         | ____%     |
| Edge Cases    | ____ / 2     | ____         | ____%     |
| **TOTAL**     | **____ / 20** | **____**    | **____%** |

### Critical Issues Found

| Issue # | Severity | Description | Steps to Reproduce |
|---------|----------|-------------|-------------------|
| 1       | ____     | __________ | _________________ |
| 2       | ____     | __________ | _________________ |
| 3       | ____     | __________ | _________________ |

Severity: P0 (Critical - blocks release), P1 (High - should fix), P2 (Medium - nice to fix), P3 (Low - cosmetic)

### Non-Critical Issues / Observations

```
________________________________________________________________
________________________________________________________________
________________________________________________________________
________________________________________________________________
```

---

## Decision: Ready for Phase 7?

Based on testing results:

- [ ] **YES** - All critical tests pass, ready for packaging (Phase 7)
- [ ] **NO** - Critical issues found, need fixes before Phase 7
- [ ] **PARTIALLY** - Minor issues acceptable, can proceed with notes

**Tester Signature**: ___________________
**Date**: ___________________

---

## Next Steps

If **YES** or **PARTIALLY**:
1. Create `PHASE-7-HANDOFF.md` in brainstorming directory
2. Begin Phase 7: Executable Packaging
3. Address minor issues during Phase 7 polish

If **NO**:
1. Document issues in detail
2. Create bug fix plan
3. Fix critical issues
4. Re-run manual testing
5. Then proceed to Phase 7
