# HANDOFF: Tag Autocomplete Focus Stealing Bug - Session 2

**Project:** Quick Snippet Overlay
**Issue:** PySide6 QCompleter popup steals focus from input field on every keystroke
**Status:** CRITICAL BUG - Feature completely unusable
**Date:** 2025-11-06
**Environment:** Windows 11, Python 3.13.1, PySide6 6.9.0

---

## 🔴 THE BUG

### Symptom
When user types in the Tags field of the Snippet Editor Dialog, **focus jumps from the input field to the dropdown popup after EACH keystroke**. User must click back into the Tags field to type the next letter.

### Expected Behavior
User should be able to type continuously (e.g., "python") while the dropdown updates in the background. Focus should NEVER leave the Tags input field.

### Current Behavior
1. User clicks in Tags field → ✅ Focus enters field
2. User types 'p' → ❌ Focus immediately jumps to dropdown
3. User must click back in Tags field
4. User types 'y' → ❌ Focus jumps to dropdown again
5. Repeat for every letter

**Result:** User cannot type more than one letter at a time. Completely unusable.

---

## 🧪 TESTING INSTRUCTIONS

### Using Puppeteer MCP (Recommended)
You have access to the `puppeteer` MCP server which can observe actual browser/application behavior. Use it to:

1. **Launch the app:**
   ```bash
   # From project root
   RUN-APP.bat
   ```

2. **Open the Snippet Editor:**
   - Right-click system tray icon (bottom-right of screen)
   - Click "Add Snippet"
   - Dialog window opens

3. **Reproduce the bug:**
   - Click in the "Tags:" field
   - Type the letter 'p'
   - **Observe:** Where does focus go after typing?
   - Try typing 'y' without clicking
   - **Observe:** Can you type continuously or must you click back?

4. **Debug observations to make:**
   - Does the dropdown popup appear? ✅ Yes, it does
   - Does the popup have focus after typing? ← **This is the question**
   - Can the user type multiple letters without clicking? ← **Currently NO**
   - Are there console logs? (Look for `[DEBUG]` messages)

### Manual Testing (Without Puppeteer)
If puppeteer can't interact with the native Qt window:
1. Ask user to test
2. Review console output from app
3. Analyze code flow

---

## 📁 CODE STRUCTURE

### Key Files

**Main Implementation:**
- `src/snippet_editor_dialog.py` (lines 24-310) - Dialog with Tags field
  - Line 24: `NoFocusListView` class (custom popup)
  - Line 40: `InputFocusProtector` class (unused event filter)
  - Line 139: `_setup_completer()` - Autocomplete setup
  - Line 218: `_on_tags_input_changed()` - Handles text input, updates popup

**Supporting Files:**
- `src/fuzzy_tag_completer.py` - Custom QCompleter subclass
- `src/snippet_manager.py` - Provides tag list via `get_all_tags()`

### Current Architecture

```
SnippetEditorDialog
  ├─ tags_input (QLineEdit) - User types here
  ├─ fuzzy_completer (FuzzyTagCompleter) - NOT attached via setCompleter()
  └─ popup (NoFocusListView) - Custom QListView
      ├─ NoFocus policy
      ├─ WA_ShowWithoutActivating flag
      └─ focusInEvent/focusOutEvent overridden to ignore()

Flow:
1. User types → tags_input.textChanged signal
2. → _on_tags_input_changed(text)
3. → Updates popup.setModel(matches)  ← Currently testing this approach
4. → popup.show() and popup.raise_()
5. → Focus stolen HERE (exact line unknown)
```

### Critical Code Section

**File:** `src/snippet_editor_dialog.py`
**Lines 218-310:** `_on_tags_input_changed()` method

```python
def _on_tags_input_changed(self, text: str):
    # Extract current tag (after last comma)
    if "," in text:
        current_tag = text.split(",")[-1].lstrip()
    else:
        current_tag = text

    # Get matches (fuzzy search logic)
    matches = [...]  # List of matching tags

    # Get popup reference
    popup = self.fuzzy_completer.popup()

    # TEST #1 (CURRENT): Update popup model directly
    model = QStringListModel(matches)
    popup.setModel(model)  # ← Bypasses QCompleter

    # Show popup
    if matches:
        if not popup.isVisible():
            input_pos = self.tags_input.mapToGlobal(self.tags_input.rect().bottomLeft())
            popup.setFixedWidth(max(self.tags_input.width(), 200))
            popup.move(input_pos)
            popup.show()      # ← Focus stolen somewhere around here?
            popup.raise_()    # ← Or here?
        # else: popup already visible, just model updated
    else:
        popup.hide()
```

---

## 🔧 ATTEMPTED FIXES (10+ attempts, all failed)

### Session 1 Attempts (Original handoff)

1. ❌ `popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)` - Focus still stolen
2. ❌ `popup.setFocusProxy(self.tags_input)` - Focus still stolen (prevented input from accepting focus)
3. ❌ `popup.setWindowFlags(Popup | FramelessWindowHint)` - Focus still stolen
4. ❌ `popup.setAttribute(WA_ShowWithoutActivating)` - Focus still stolen
5. ❌ `self.tags_input.setFocus()` after popup.show() - Focus still stolen
6. ❌ `QTimer.singleShot(0, lambda: self.tags_input.setFocus())` - Focus still stolen
7. ❌ Removed `setCurrentIndex()` call - Focus still stolen
8. ❌ Only call `popup.show()` once - Focus still stolen on first keystroke

### Session 2 Attempts (Current)

9. ❌ **Custom NoFocusListView class** - Created subclass overriding focusInEvent/focusOutEvent with `event.ignore()` - Focus still stolen

10. ❌ **InputFocusProtector event filter** - Blocked FocusOut events on tags_input - Prevented input from accepting focus (had to remove)

11. ❌ **Bypass QCompleter.setModel()** - Update popup.setModel() directly instead of completer.setModel() - **CURRENTLY ACTIVE, still fails**

### Why These Failed

All attempts tried to fight Qt's focus system at the property/flag level. Qt's internal event handling appears to override these settings.

---

## 🎯 NEXT STEPS TO TRY

### Test #2: Explicit Focus Restoration (Not Yet Tried)

**Theory:** `popup.show()` or `popup.raise_()` activates the window despite flags. Force focus back immediately.

**Implementation:**
```python
# In _on_tags_input_changed(), after popup.show():
popup.show()
popup.raise_()
self.tags_input.setFocus(Qt.FocusReason.OtherFocusReason)
QApplication.processEvents()  # Process focus change immediately
```

**File:** `src/snippet_editor_dialog.py` line ~298

### Test #3: Change event.ignore() to event.accept() (Not Yet Tried)

**Theory:** `event.ignore()` means "pass to parent" which might confuse Qt. `event.accept()` means "handled, do nothing."

**Implementation:**
```python
class NoFocusListView(QListView):
    def focusInEvent(self, event):
        event.accept()  # Tell Qt we handled it
        # Don't call super() - prevents view from taking focus
```

**File:** `src/snippet_editor_dialog.py` line 31

### Test #4: Disable popup entirely and use QMenu (Nuclear Option)

**Theory:** QCompleter/QListView is fundamentally broken. Use QMenu for dropdown instead.

**Implementation:**
- Replace `QListView` popup with `QMenu`
- Manually add QAction items for each tag
- Position below tags_input
- Connect actions to insert tags

**Reference:** Standard Qt pattern for custom dropdowns

### Test #5: Re-enable QCompleter on widget with custom completion mode

**Theory:** Fighting Qt is wrong approach. Use QCompleter properly but override specific behaviors.

**Implementation:**
```python
self.tags_input.setCompleter(self.fuzzy_completer)
# But intercept completion signals to prevent auto-insertion
```

---

## 🐛 DEBUGGING STRATEGY

### Step 1: Identify EXACT line where focus is stolen

Add focus debugging:

```python
def _on_tags_input_changed(self, text: str):
    print(f"[FOCUS DEBUG] Start - Focus on: {QApplication.focusWidget()}")

    # ... existing code ...

    popup.setModel(model)
    print(f"[FOCUS DEBUG] After setModel - Focus on: {QApplication.focusWidget()}")

    popup.show()
    print(f"[FOCUS DEBUG] After show - Focus on: {QApplication.focusWidget()}")

    popup.raise_()
    print(f"[FOCUS DEBUG] After raise - Focus on: {QApplication.focusWidget()}")
```

**Expected output:** Focus should stay on tags_input (QLineEdit)
**Actual output:** Focus changes to popup (NoFocusListView) at some point

### Step 2: Check Qt event flow

Install event filter that logs ALL events:

```python
class DebugEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() in [QEvent.Type.FocusIn, QEvent.Type.FocusOut,
                           QEvent.Type.WindowActivate, QEvent.Type.Show]:
            print(f"[EVENT] {obj.__class__.__name__}: {event.type()}")
        return False

# Install on both tags_input and popup
debug_filter = DebugEventFilter()
self.tags_input.installEventFilter(debug_filter)
popup.installEventFilter(debug_filter)
```

### Step 3: Test on different platforms

If possible, test on Linux or macOS to see if it's Windows-specific behavior.

---

## 💡 INSIGHTS & HYPOTHESES

### Why This Is So Hard

1. **Qt's focus system is complex:** Multiple layers (widget focus, window activation, focus chain, focus policy)
2. **QCompleter has internal magic:** Even without setCompleter(), it might have event handlers
3. **PySide6 vs PyQt6:** Possible differences in focus handling between bindings
4. **Windows-specific:** Window activation behavior differs across platforms

### Possible Root Causes

**Hypothesis A:** `popup.show()` activates the popup window despite `WA_ShowWithoutActivating`
**Evidence:** All other flags/properties have been tried and failed
**Test:** Add `self.tags_input.setFocus()` + `processEvents()` immediately after show()

**Hypothesis B:** `popup.setModel()` triggers internal QListView logic that changes focus
**Evidence:** Test #1 tried this, still failed
**Counter-test:** Don't show popup at all, see if model update alone steals focus

**Hypothesis C:** The popup being a child window causes OS-level window activation
**Evidence:** Popup is a separate Qt.WindowType.Popup window
**Test:** Set popup parent explicitly: `popup.setParent(self)` with appropriate flags

---

## 📋 CURRENT CODE STATE

### NoFocusListView (Lines 24-37)

```python
class NoFocusListView(QListView):
    """Custom QListView that refuses to accept focus, preventing focus stealing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def focusInEvent(self, event):
        """Override to ignore focus events and prevent focus stealing."""
        event.ignore()

    def focusOutEvent(self, event):
        """Override to ignore focus events."""
        event.ignore()
```

### Completer Setup (Lines 164-184)

```python
# Replace default popup with custom NoFocusListView
custom_popup = NoFocusListView()
custom_popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
# DON'T set focus proxy - it interferes with normal focus behavior

# Set window flags to prevent focus stealing
custom_popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
custom_popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

# Set the custom popup on the completer
self.fuzzy_completer.setPopup(custom_popup)

# Get reference to our custom popup for later use
popup = self.fuzzy_completer.popup()

popup.clicked.connect(lambda index: self._on_completion_selected(
    self.fuzzy_completer.model().data(index, Qt.ItemDataRole.DisplayRole)
))

# DON'T install event filter - the NoFocusListView alone is sufficient
# Event filter was preventing tags_input from accepting focus
```

### Test #1 Implementation (Lines 279-287)

```python
# Get popup reference first
popup = self.fuzzy_completer.popup()

# TEST #1: Update popup model directly instead of completer model
# This bypasses QCompleter's internal logic that might steal focus
model = QStringListModel(matches)
popup.setModel(model)  # Direct model update on popup, not completer

print(f"[DEBUG] Model updated directly on popup (bypassing completer)")
```

---

## 🧪 TESTS TO VERIFY FIX

### Test Case 1: Continuous Typing
```
1. Click in Tags field
2. Type: python (6 letters continuously, no clicking)
3. PASS: All 6 letters typed without clicking back
4. FAIL: Had to click back after any letter
```

### Test Case 2: Focus Never Leaves
```
1. Click in Tags field
2. Type: p
3. Check: Is cursor still in Tags field? (blinks/visible)
4. Type: y (without clicking)
5. Check: Typed "py" successfully?
```

### Test Case 3: Dropdown Updates
```
1. Type: p
2. Check: Dropdown shows (python, pyside, etc.)
3. Type: y (without clicking)
4. Check: Dropdown updates to show (python, pyside)
5. Check: Focus still in Tags field
```

---

## 🔍 FILES TO REVIEW

### Primary
- `src/snippet_editor_dialog.py` (Lines 139-310) - The entire autocomplete system

### Secondary
- `src/fuzzy_tag_completer.py` - Custom QCompleter (might have internal issues)
- `tests/test_snippet_editor_dialog.py` - Tests (all passing, but don't test focus)

### Documentation
- `HANDOFF-TAG-AUTOCOMPLETE-FOCUS-ISSUE.md` - Original handoff
- `FOCUS-FIX-IMPLEMENTATION.md` - First attempt documentation
- `FOCUS-FIX-SIMPLIFIED.md` - Second attempt documentation

---

## 🎬 QUICKSTART FOR NEW SESSION

1. **Read this document fully**
2. **Use puppeteer to observe the bug:** Launch app, open dialog, watch focus behavior
3. **Add focus debugging:** Insert print statements to identify exact line where focus stolen
4. **Try Test #2:** Explicit focus restoration with processEvents()
5. **If Test #2 fails, try Test #3:** Change event.ignore() to event.accept()
6. **If all fails, nuclear option:** Replace QCompleter/QListView with QMenu

---

## 💬 USER QUOTE

> "I enter a letter in the tags form box. Immediately the focus changes to the first word on the list that is generated. To enter a second letter, I have to mouse up to the form box to set the cursor and enter a second letter. What I want is for the focus to stay in the form box for tags after every letter."

This has been explained multiple times. User is frustrated. **This is the blocking issue for Phase 5 completion.**

---

## ✅ WHAT WORKS (Don't Break These)

- ✅ Tag matching (fuzzy search)
- ✅ Dropdown appearance
- ✅ Click/Enter selection from dropdown
- ✅ Comma-separated multi-tag input
- ✅ No auto-insertion of first match
- ✅ All 14 unit tests passing

---

## 📊 ENVIRONMENT

- **OS:** Windows 11
- **Python:** 3.13.1
- **PySide6:** 6.9.0 (NOT PyQt6)
- **Qt Runtime:** 6.10.0
- **Project:** `C:\Users\mikeh\software_projects\quick-snippet-overlay`
- **Run Command:** `RUN-APP.bat` (activates venv, launches app)
- **Venv:** `.venv\Scripts\python.exe`

---

## 🚀 SUCCESS CRITERIA

User can type "python" continuously in Tags field without clicking back. Dropdown updates in background. Focus NEVER leaves Tags input field.

**If you solve this, you're a hero.** 🦸

---

**Generated:** 2025-11-06
**Session:** 2
**Priority:** P0 - BLOCKING
**Confidence:** Use puppeteer to observe actual behavior and identify exact failure point
