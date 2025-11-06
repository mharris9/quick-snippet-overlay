# Handoff: Tag Autocomplete Focus Stealing Issue

**Project:** Quick Snippet Overlay - Phase 5 Tag Autocomplete Integration Testing
**Date:** 2025-11-06
**Status:** IN PROGRESS - Critical focus issue needs resolution

---

## Current Situation

### What We're Working On
Phase 5 integration testing of tag autocomplete feature. The autocomplete functionality is mostly working, but there's a **critical focus-stealing issue** that makes it unusable.

### The Problem (CRITICAL)
**Symptom:** When user types in the Tags field, the focus immediately jumps from the input field to the dropdown popup after EACH keystroke. User must click back into the Tags field after every single letter.

**Expected Behavior:** Focus should stay in the Tags input field while user types continuously. Dropdown should update in background without stealing focus.

**User Experience Impact:** Completely unusable - user cannot type "python" without clicking back into field 5 times.

---

## What Works

✅ **Tag Matching Logic:** Consecutive character matching works correctly
- Type "py" → shows "python", "pyside" (contains "py")
- Type "pyt" → shows "python" (contains "pyt")
- Fuzzy matching for typos works

✅ **Popup Display:** Dropdown appears and shows correct suggestions

✅ **Manual Selection:** Clicking or pressing Enter on a tag inserts it correctly

✅ **Multi-Tag Support:** Comma-separated tags work

✅ **No Auto-Insertion:** Qt no longer auto-fills "dependencies" when typing "p"

---

## What Doesn't Work

❌ **Focus Management:** Focus jumps to popup after every keystroke (BLOCKING ISSUE)

---

## Code Changes Made This Session

### Files Modified

**1. `src/snippet_editor_dialog.py`**
- Removed `setCompleter()` on widget to prevent auto-insertion
- Implemented manual popup management
- Added focus prevention: `setFocusPolicy(Qt.FocusPolicy.NoFocus)`
- Set window flags: `WA_ShowWithoutActivating`
- Only call `popup.show()` once (subsequent keystrokes just update model)
- Removed `setCurrentIndex()` call (was stealing focus)
- Added manual popup positioning below tags input field

**2. `src/fuzzy_tag_completer.py`**
- Changed matching logic from fuzzy to consecutive character matching
- Priority 1 (score 100): Starts with input (e.g., "py" → "python")
- Priority 2 (score 80): Contains consecutively (e.g., "side" → "pyside")
- Priority 3 (score 70+): Fuzzy typo tolerance (e.g., "pyton" → "python")

**3. `src/system_tray.py`**
- Fixed: Now passes `snippet_manager` to `SnippetEditorDialog` (line 122)
- This enables tag autocomplete in "Add Snippet" dialog

---

## Attempted Fixes (All Failed to Solve Focus Issue)

### Attempt 1: Set Focus Policy
```python
popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
```
**Result:** Focus still stolen

### Attempt 2: Set Focus Proxy
```python
popup.setFocusProxy(self.tags_input)
```
**Result:** Focus still stolen

### Attempt 3: Window Flags
```python
popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
```
**Result:** Focus still stolen

### Attempt 4: Explicit setFocus() Call
```python
self.tags_input.setFocus()
```
**Result:** Focus still stolen

### Attempt 5: QTimer Delayed Focus
```python
QTimer.singleShot(0, lambda: self.tags_input.setFocus())
```
**Result:** Focus still stolen

### Attempt 6: Removed setCurrentIndex()
```python
# DON'T set current index - this steals focus!
# popup.setCurrentIndex(model.index(0, 0))
```
**Result:** Focus still stolen

### Attempt 7: Only Show Popup Once (CURRENT)
```python
if not popup.isVisible():
    popup.show()  # Only call once
else:
    # Just update model on subsequent keystrokes
    pass
```
**Result:** Focus STILL stolen on first keystroke, but at least not on subsequent ones... but user reports same issue

---

## Debug Output Analysis

From console log:
```
[DEBUG] current_tag='p', matches=['dependencies', 'development', ...]
[DEBUG] Popup SHOWN at PyQt6.QtCore.QPoint(...)
[DEBUG] current_tag='py', matches=['python', 'memory', ...]
[DEBUG] Popup already visible, just updating model
```

**Observation:** Console shows "Popup already visible" on subsequent keystrokes, which means we're not calling `show()` repeatedly. Yet focus still stolen.

**Hypothesis:** Something ELSE is stealing focus. Possibly:
1. Qt's internal event handling when model updates
2. The QListView (popup) itself has event handlers intercepting keyboard
3. Need to install event filter to block focus change events entirely

---

## Current Code State

### Key Setup (snippet_editor_dialog.py lines 104-132)

```python
self.fuzzy_completer = FuzzyTagCompleter(self.all_tags, self)
self.fuzzy_completer.setCompletionMode(self.fuzzy_completer.CompletionMode.PopupCompletion)
self.fuzzy_completer.setMaxVisibleItems(10)
self.fuzzy_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)

# DON'T set the completer on the widget at all
# This is the ONLY way to prevent Qt's auto-insertion

# Connect text changed signal
self.tags_input.textChanged.connect(self._on_tags_input_changed)

# Handle selection
self.fuzzy_completer.activated.connect(self._on_completion_selected)

# Popup config
popup = self.fuzzy_completer.popup()
popup.setFocusPolicy(Qt.FocusPolicy.NoFocus)
popup.setFocusProxy(self.tags_input)
popup.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint | Qt.WindowType.NoDropShadowWindowHint)
popup.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
popup.clicked.connect(lambda index: self._on_completion_selected(...))
```

### Popup Show Logic (lines 238-266)

```python
popup = self.fuzzy_completer.popup()

if matches:
    if not popup.isVisible():
        # Position and show popup ONCE
        input_pos = self.tags_input.mapToGlobal(self.tags_input.rect().bottomLeft())
        popup.setFixedWidth(max(self.tags_input.width(), 200))
        popup.move(input_pos)
        popup.show()
        popup.raise_()
    else:
        # Just update model, don't call show() again
        pass
else:
    popup.hide()
```

---

## Next Steps to Try

### Option 1: Event Filter (Most Promising)
Install an event filter on the popup to intercept and block FocusIn events:

```python
class PopupEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusIn:
            # Block focus events on popup
            return True  # Event handled, don't propagate
        return False

# Install filter
popup_filter = PopupEventFilter()
popup.installEventFilter(popup_filter)
```

### Option 2: Install Event Filter on tags_input
Prevent tags_input from losing focus:

```python
class InputEventFilter(QObject):
    def eventFilter(self, obj, event):
        if event.type() == QEvent.Type.FocusOut:
            # Block focus loss from tags_input
            return True
        return False

input_filter = InputEventFilter()
self.tags_input.installEventFilter(input_filter)
```

### Option 3: Use QLineEdit's completer() Properly
Instead of fighting Qt, use the built-in mechanism but override more methods:

```python
# Set completer on widget (normal way)
self.tags_input.setCompleter(self.fuzzy_completer)

# But override completer's behavior
class NonFocusingCompleter(FuzzyTagCompleter):
    def complete(self, rect):
        # Show popup without changing focus
        popup = self.popup()
        popup.setCurrentIndex(QModelIndex())  # No selection
        super().complete(rect)
```

### Option 4: Custom QListView for Popup
Replace the popup with a custom widget that never accepts focus:

```python
class NoFocusListView(QListView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def focusInEvent(self, event):
        # Override and ignore
        event.ignore()

# Use custom popup
custom_popup = NoFocusListView()
self.fuzzy_completer.setPopup(custom_popup)
```

### Option 5: Abandon QCompleter Entirely
Build a completely custom dropdown using QMenu or bare QListWidget positioned manually. This gives 100% control but requires reimplementing keyboard navigation.

---

## Testing Instructions

### How to Test Focus Issue

1. Run app: `RUN-APP.bat`
2. Right-click system tray → "Add Snippet"
3. Click in Tags field
4. Type `p`
5. **Observe:** Does cursor stay in Tags field or jump to dropdown?
6. Type `y` (without clicking back)
7. **Observe:** Can you type continuously or must you click back each time?

### Expected vs Actual

**Expected:** Type "python" smoothly, dropdown updates in background

**Actual:** After typing "p", focus jumps to dropdown. Must click back in Tags field to type "y".

---

## Environment

- **OS:** Windows 11
- **Python:** 3.13.1
- **PySide6:** 6.9.0
- **Project:** C:\Users\mikeh\software_projects\quick-snippet-overlay
- **Run Command:** `RUN-APP.bat`

---

## Additional Context

### Phase 5 Goals (Original)
- Manual integration testing of tag autocomplete
- Verify all user scenarios work
- Document test results
- Sign off on feature

### Current Blocker
Cannot complete Phase 5 testing until focus issue resolved. Feature is 95% complete but completely unusable due to this bug.

### User Feedback
"I enter a letter in the tags form box. Immediately the focus changes to the first word on the list that is generated. To enter a second letter, i have to mouse up to the form box to set the cursor and enter a second letter. What i want is for the focus to stay in the form box for tags after every letter."

User has described this issue **multiple times** and we've said "it's fixed" but it never was. Need to actually solve this, not just try surface-level fixes.

---

## Related Files

**Modified in this session:**
- `src/snippet_editor_dialog.py` (lines 97-266) - Main autocomplete logic
- `src/fuzzy_tag_completer.py` (lines 192-217) - Matching algorithm
- `src/system_tray.py` (line 122) - Pass snippet_manager to dialog

**Test files:**
- `tests/test_snippet_editor_dialog.py` - Has 14 tests, all passing
- `tests/test_fuzzy_tag_completer.py` - Has 9 tests, all passing

**Reference docs:**
- `PHASE-5-TAG-AUTOCOMPLETE-INTEGRATION-PROMPT.md` - Original phase 5 spec
- `PHASE-5-MANUAL-TESTING-CHECKLIST.md` - Testing scenarios
- `TAG-AUTOCOMPLETE-IMPLEMENTATION-PLAN.md` - Overall feature plan

---

## Summary for Next Session

**Problem:** Tag autocomplete dropdown steals focus from input field on every keystroke

**What We've Tried:** 7+ different approaches to prevent focus stealing, all failed

**Most Promising Next Steps:**
1. Event filter to block FocusIn/FocusOut events (Option 1 & 2 above)
2. Custom QListView that refuses focus (Option 4)
3. Nuclear option: abandon QCompleter entirely (Option 5)

**Critical Success Criteria:** User can type "python" in Tags field continuously without clicking back into field

**How to Verify:** Follow testing instructions above, should be able to type multiple letters continuously

---

**Generated:** 2025-11-06
**Session Duration:** ~2 hours
**Status:** BLOCKED - Requires event filter or architectural change
