# Test Execution Guide - Manual Integration Testing

**Status**: Ready to Begin
**Estimated Time**: 30-60 minutes
**Date**: 2025-11-04

---

## Quick Start

### Step 1: Launch the Application

Open PowerShell in the project directory and run:

```powershell
cd C:\Users\mikeh\software_projects\quick-snippet-overlay
.\RUN-APP.ps1
```

**What to expect**:
- Console shows "Launching Quick Snippet Overlay..."
- System tray icon appears in Windows taskbar (bottom-right)
- No errors in console
- Application ready to use

**If errors occur**: Check the console output for details. Common issues:
- Missing dependencies → Run `pip install -r requirements.txt`
- Port conflicts → Check if another instance is running
- Missing files → Application should create defaults

---

### Step 2: Quick Smoke Test (5 minutes)

**Objective**: Verify core functionality works

1. **System Tray Icon**:
   - [ ] Look in taskbar notification area (bottom-right)
   - [ ] System tray icon visible
   - [ ] Right-click icon shows context menu

2. **Open Overlay**:
   - [ ] Press **Ctrl+Shift+Space** (global hotkey)
   - [ ] Overlay window appears centered on screen
   - [ ] Search box has focus (can type immediately)

3. **Search**:
   - [ ] Type "git" in search box
   - [ ] Results appear (should show "Undo last commit", "Force push with lease")
   - [ ] Results update as you type

4. **Copy Snippet**:
   - [ ] Select a simple snippet (e.g., "Install Python requirements")
   - [ ] Press Enter
   - [ ] Overlay closes
   - [ ] Open Notepad and press Ctrl+V
   - [ ] Snippet content pasted correctly

5. **Exit**:
   - [ ] Right-click system tray icon
   - [ ] Click "Exit"
   - [ ] Icon disappears from tray
   - [ ] Application terminates cleanly

**Result**: ✅ PASS / ❌ FAIL

If all items pass, core functionality is working! Continue with comprehensive testing below.

---

## Comprehensive Testing

For detailed test cases, refer to `MANUAL-TESTING-GUIDE.md` in this directory.

### Test Categories:

#### 1. Core Features (Tests 1-12)
Essential functionality that must work for v1.0:
- Application startup
- System tray integration
- Overlay display and positioning
- Global hotkey activation
- Fuzzy search
- Snippet copying
- Variable substitution
- Edit/reload snippets
- Single instance enforcement
- Graceful exit

**Priority**: CRITICAL - Must pass 100%

---

#### 2. Error Handling (Tests Error 1-3)
How application handles problems:
- Corrupted YAML files
- Missing snippet files
- Hotkey conflicts

**Priority**: HIGH - Should handle gracefully without crashes

---

#### 3. Performance (Tests Performance 1-3)
Speed and resource usage:
- Startup time (<2 seconds)
- Search latency (<50ms)
- Memory usage (<100MB idle)

**Priority**: MEDIUM - Should meet targets, minor deviations acceptable

---

#### 4. Edge Cases (Tests Edge 1-2)
Less common scenarios:
- Multi-monitor support
- Windows scaling
- Special characters

**Priority**: LOW - Nice to have, not blocking

---

## Testing Workflow

### Option A: Full Test Suite (45-60 minutes)

Complete all tests in `MANUAL-TESTING-GUIDE.md`:

```powershell
# 1. Open the test guide
notepad.exe MANUAL-TESTING-GUIDE.md

# 2. Launch application
.\RUN-APP.ps1

# 3. Work through each test section
# 4. Record results in the guide (print or fill PDF)
# 5. Document any issues found
```

**When to use**: Before Phase 7 packaging, or for thorough validation

---

### Option B: Critical Path Testing (15-20 minutes)

Test only the essential user workflow:

1. **Launch Application**
2. **Test Core Workflow**:
   - Press Ctrl+Shift+Space
   - Search for snippet
   - Select and copy
   - Paste in target app
3. **Test Variable Substitution**:
   - Find snippet with `{{variable:default}}` syntax
   - Enter custom values
   - Verify substitution
4. **Test Hot-Reload**:
   - Edit `C:\Users\mikeh\snippets\snippets.yaml`
   - Add new snippet
   - Verify it appears without restart
5. **Test Error Recovery**:
   - Introduce YAML syntax error
   - Verify graceful error message
   - Fix and reload
6. **Clean Exit**

**When to use**: Quick validation after bug fixes or minor changes

---

### Option C: Exploratory Testing (30 minutes)

Free-form testing to discover unexpected issues:

1. Launch application
2. Use it naturally for real tasks
3. Try edge cases:
   - Very long search queries
   - Rapid hotkey presses
   - Editing snippets while app running
   - Using in different applications
   - Switching between monitors
4. Note anything that feels wrong or broken

**When to use**: After critical path testing passes, to find hidden issues

---

## Recording Test Results

### During Testing

Keep notes on:
- **Passed Tests**: Quick checkmark ✅
- **Failed Tests**: Note what happened, expected vs actual
- **Performance Observations**: Slow? Fast? Laggy?
- **Usability Issues**: Confusing? Hard to use?
- **Ideas**: Features you wish existed

### Test Results Template

Create a file `TEST-RESULTS-2025-11-04.md` with:

```markdown
# Test Results - 2025-11-04

## Environment
- Windows Version: _______
- Screen Resolution: _______
- Python Version: _______

## Quick Summary
- Tests Passed: ____ / ____
- Tests Failed: ____
- Critical Issues: ____
- Minor Issues: ____

## Critical Issues (P0)
1. [Description] - [Steps to reproduce]

## High Priority Issues (P1)
1. [Description] - [Steps to reproduce]

## Observations / Notes
- [Any feedback, ideas, or observations]

## Decision
- [ ] Ready for Phase 7 (packaging)
- [ ] Needs fixes before Phase 7
- [ ] Needs more testing

## Next Steps
[What should happen next based on results]
```

---

## Common Issues and Solutions

### Issue: Application won't start

**Symptoms**: Script exits immediately or shows errors

**Solutions**:
1. Check Python version: `python --version` (need 3.10+)
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check for another instance: Task Manager → find python.exe → End task
4. Delete lock file: `C:\Users\mikeh\AppData\Local\QuickSnippetOverlay\app.lock`

---

### Issue: Hotkey doesn't work

**Symptoms**: Ctrl+Shift+Space does nothing

**Solutions**:
1. Check console for error messages
2. Try from different application (some apps capture hotkeys)
3. Check if another app uses same hotkey
4. Try editing config.yaml to use different hotkey:
   ```yaml
   hotkey: ctrl+alt+space
   ```
5. Restart application

---

### Issue: System tray icon missing

**Symptoms**: No icon in taskbar

**Solutions**:
1. Check Windows notification area settings:
   - Right-click taskbar → Taskbar settings
   - Notification area → Select which icons appear
   - Find Python and set to "Show icon and notifications"
2. Try clicking "Show hidden icons" (^) in taskbar
3. Check console for startup errors

---

### Issue: Overlay appears on wrong monitor

**Symptoms**: Window shows on secondary monitor

**Solutions**:
- Currently expected behavior (appears on primary monitor)
- Workaround: Set display as primary in Windows settings
- Note as enhancement for future version

---

### Issue: Search results seem wrong

**Symptoms**: Expected snippet doesn't appear in results

**Check**:
1. Spelling (fuzzy search tolerates typos, but has limits)
2. Is snippet in `C:\Users\mikeh\snippets\snippets.yaml`?
3. Try searching by tag instead of name
4. Try partial match (first few letters)
5. Reload snippets (right-click tray → Reload Snippets)

---

## After Testing

### If All Tests Pass ✅

1. **Document Success**:
   - Fill out test results template
   - Note any minor issues (non-blocking)
   - Capture performance metrics

2. **Create Test Report**:
   ```markdown
   # Phase 6 Integration Test Report - PASSED

   Date: 2025-11-04
   Tester: [Your name]
   Duration: [X minutes]

   ## Summary
   All critical tests passed. Application ready for Phase 7 (packaging).

   ## Test Results
   - Core Features: 12/12 passed
   - Error Handling: 3/3 passed
   - Performance: 3/3 passed
   - Edge Cases: 2/2 passed

   ## Performance Metrics
   - Startup time: [X.X seconds]
   - Search latency: Instant (<50ms)
   - Memory usage: [XX MB]

   ## Minor Issues (Acceptable)
   - [List any minor issues that don't block release]

   ## Recommendation
   PROCEED to Phase 7 - Polish & Packaging
   ```

3. **Next Step**: Ready for Phase 7!

---

### If Critical Tests Fail ❌

1. **Document Failures**:
   - Which tests failed
   - Exact error messages
   - Steps to reproduce
   - Screenshots if helpful

2. **Categorize Issues**:
   - **P0 (Critical)**: Application crashes, core features broken
   - **P1 (High)**: Important features don't work, bad UX
   - **P2 (Medium)**: Minor issues, workarounds exist
   - **P3 (Low)**: Cosmetic issues, enhancements

3. **Create Bug List**:
   ```markdown
   # Bug Report - Phase 6 Integration Testing

   ## Critical Bugs (P0)

   ### Bug 1: [Title]
   - Severity: P0
   - Description: [What's broken]
   - Steps to Reproduce:
     1. [Step 1]
     2. [Step 2]
   - Expected: [What should happen]
   - Actual: [What actually happens]
   - Error Messages: [Any console output]

   ## High Priority Bugs (P1)
   [Same format]
   ```

4. **Fix Bugs**:
   - Address P0 issues immediately
   - Fix P1 issues if time permits
   - Note P2/P3 for future versions

5. **Retest**:
   - After fixes, re-run failed tests
   - Verify fixes don't break other features
   - Update test results

6. **Decide**:
   - All P0 fixed → Proceed to Phase 7
   - P0 still failing → More debugging needed

---

## Tips for Effective Testing

### Do:
- ✅ Test on clean state (fresh snippets, default config)
- ✅ Take notes as you go (easy to forget issues)
- ✅ Test like a real user (natural usage patterns)
- ✅ Try to break it (edge cases reveal bugs)
- ✅ Test in different applications (Notepad, VS Code, browser, etc.)

### Don't:
- ❌ Skip tests because "it probably works"
- ❌ Ignore minor issues (document everything)
- ❌ Test too fast (give app time to respond)
- ❌ Only test happy path (errors happen!)

---

## Ready to Start?

1. **Review**: Scan through `MANUAL-TESTING-GUIDE.md`
2. **Launch**: Run `.\RUN-APP.ps1`
3. **Test**: Work through Quick Smoke Test first
4. **Document**: Record results as you go
5. **Report**: Summarize findings

**Estimated Total Time**:
- Quick Smoke Test: 5 minutes
- Critical Path: 15-20 minutes
- Full Test Suite: 45-60 minutes

**Choose your testing approach and begin!**

Good luck! 🚀
