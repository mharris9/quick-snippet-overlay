# Focus-Stealing Issue - Simplified Fix ✅

**Date:** 2025-11-06
**Status:** READY FOR TESTING
**Approach:** Single-layer defense (NoFocusListView only)

---

## Problem

The initial two-layer fix (NoFocusListView + InputFocusProtector) was preventing the Tags field from accepting focus when clicked. Users couldn't type in the field at all.

**Root Cause:** The `InputFocusProtector` event filter and `setFocusProxy()` were interfering with normal focus behavior.

---

## Simplified Solution

**Remove Layer 2 entirely** - The `NoFocusListView` alone is sufficient to prevent focus stealing.

### What Was Removed

1. ❌ Removed `setFocusProxy(self.tags_input)` call
2. ❌ Removed `InputFocusProtector` event filter installation
3. ✅ Kept `NoFocusListView` class (Layer 1)

### Why NoFocusListView Alone Works

```python
class NoFocusListView(QListView):
    """Custom QListView that refuses to accept focus, preventing focus stealing."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.NoFocus)

    def focusInEvent(self, event):
        """Override to ignore focus events and prevent focus stealing."""
        event.ignore()  # Refuse to accept focus

    def focusOutEvent(self, event):
        """Override to ignore focus events."""
        event.ignore()
```

**How it works:**
- When Qt tries to give focus to the popup, `focusInEvent()` is called
- By calling `event.ignore()`, we tell Qt "I don't want focus"
- Qt keeps focus on the current widget (tags_input)
- Result: Focus stays in tags_input while dropdown updates

---

## Code Changes (from previous version)

### src/snippet_editor_dialog.py

**Line 167:** Removed setFocusProxy
```python
# BEFORE:
custom_popup.setFocusProxy(self.tags_input)

# AFTER:
# DON'T set focus proxy - it interferes with normal focus behavior
```

**Lines 183-185:** Removed event filter
```python
# BEFORE:
self.focus_protector = InputFocusProtector(self)
self.tags_input.installEventFilter(self.focus_protector)

# AFTER:
# DON'T install event filter - the NoFocusListView alone is sufficient
# Event filter was preventing tags_input from accepting focus
```

---

## Test Results

All 14 tests passing ✅

```
============================= 14 passed in 1.63s ==============================
Test Coverage: 80% for snippet_editor_dialog.py
```

---

## Manual Testing Instructions

### Test 1: Field Accepts Focus
1. Run `RUN-APP.bat`
2. Right-click system tray → "Add Snippet"
3. **Click in Tags field**
4. **Expected:** Cursor appears, field is active
5. **Success:** You can type immediately

### Test 2: Focus Stays While Typing
1. With cursor in Tags field, type: `python`
2. **Expected:** All 6 letters typed continuously, no clicking back needed
3. **Success:** Dropdown updates in background without stealing focus

### Test 3: Navigation Between Fields
1. Click in Name field
2. Click in Tags field
3. Click in Content field
4. Click back in Tags field
5. **Expected:** All clicks work normally
6. **Success:** Focus moves as expected

### Test 4: Dropdown Interaction
1. Type `p` in Tags field
2. **Expected:** Dropdown shows, focus stays in Tags field
3. Use arrow keys to navigate dropdown
4. Press Enter to select
5. **Expected:** Tag inserted, focus returns to Tags field
6. **Success:** Can immediately type comma and next tag

---

## Why This Is Better

### Previous (Two-Layer)
❌ NoFocusListView + InputFocusProtector
❌ Event filter blocked normal focus changes
❌ Tags field couldn't accept focus

### Current (Single-Layer)
✅ NoFocusListView only
✅ Normal focus behavior preserved
✅ Tags field works normally
✅ Popup still can't steal focus

---

## Technical Details

### Why InputFocusProtector Failed

The `InputFocusProtector` was filtering `FocusOut` events on `tags_input`. The logic checked if focus was moving to `NoFocusListView` and blocked it. However, this had unintended side effects:

1. Interfered with focus chain when clicking into tags_input from other fields
2. Created race conditions with Qt's focus management
3. Was redundant - NoFocusListView already refuses focus at the widget level

### Why setFocusProxy Failed

`setFocusProxy(self.tags_input)` told the popup: "If you get focus, redirect it to tags_input." But since the popup has `NoFocus` policy and refuses focus in `focusInEvent()`, this created a confusing state where Qt didn't know where to put focus.

### Why NoFocusListView Alone Works

It operates at the **widget event handler level**, which is the lowest level before Qt's focus system processes the change. When Qt tries to move focus to the popup:

1. Qt calls `popup.focusInEvent(event)`
2. We call `event.ignore()`
3. Qt sees the event was ignored and doesn't change focus
4. Focus stays where it was (tags_input)

No event filters, no focus proxies, no interference with normal behavior.

---

## Files Modified

- `src/snippet_editor_dialog.py` - Removed setFocusProxy and event filter
- `tests/test_snippet_editor_dialog.py` - Tests still pass (no changes needed)
- `FOCUS-FIX-SIMPLIFIED.md` - This document

---

## Confidence Level

**HIGH** - Simpler is better. Single point of control, no interference with Qt's focus system.

---

## What to Keep

✅ **NoFocusListView class** - The core solution
✅ **InputFocusProtector class** - Can remove entirely if not used elsewhere

## What to Remove (Optional Cleanup)

The `InputFocusProtector` class (lines 40-61) is no longer used and can be safely deleted if you want to clean up the code.

---

**Status:** Ready for testing

**Next Steps:**
1. Test that Tags field accepts focus when clicked
2. Test that focus doesn't jump while typing
3. Test that dropdown interaction works
4. If all tests pass, clean up unused InputFocusProtector class

---

**Generated:** 2025-11-06
**Fix Time:** 10 minutes
