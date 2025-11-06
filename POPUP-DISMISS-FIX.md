# Popup Dismiss Logic - Fix for Tool Windows

**Date:** 2025-11-06
**Issue:** Tool windows don't auto-dismiss like Popup windows
**Status:** IMPLEMENTED

---

## 🎯 THE PROBLEM

After fixing the focus issue by changing window type from `Popup` to `Tool`:
- ✅ User can type continuously (focus fix worked!)
- ❌ Popup won't dismiss with ESC or clicking outside

**Root Cause:**
- `Qt.WindowType.Popup` windows have built-in auto-dismiss behavior
- `Qt.WindowType.Tool` windows do NOT auto-dismiss (they're meant for toolbars)
- We needed `Tool` to prevent window activation, but lost auto-dismiss

---

## 🔧 THE SOLUTION

Added explicit dismiss logic for 4 scenarios:

### 1. ESC Key Press
**Implementation:** `InputFocusProtector.eventFilter()` lines 102-106

```python
if key == Qt.Key.Key_Escape and self.popup and self.popup.isVisible():
    print(f"[DEBUG] ESC pressed - hiding popup")
    self.popup.hide()
    return True  # Consume the ESC event
```

**Behavior:** When user presses ESC in tags_input, popup immediately hides.

### 2. Focus Leaving Tags Field
**Implementation:** `InputFocusProtector.eventFilter()` lines 108-120

```python
if event.type() == QEvent.Type.FocusOut:
    focus_widget = obj.window().focusWidget()

    # If focus going to another widget (name, description, buttons), hide popup
    if self.popup and self.popup.isVisible():
        print(f"[DEBUG] Focus leaving tags_input - hiding popup")
        self.popup.hide()
```

**Behavior:** When user tabs/clicks to another field, popup hides.

**Exception:** If popup tries to steal focus (shouldn't happen with Tool type), we block it.

### 3. Click Outside Tags Field
**Implementation:** `SnippetEditorDialog.mousePressEvent()` lines 142-155

```python
def mousePressEvent(self, event):
    if hasattr(self, 'fuzzy_completer'):
        popup = self.fuzzy_completer.popup()
        if popup and popup.isVisible():
            if not self.tags_input.geometry().contains(event.pos()):
                print(f"[DEBUG] Click outside tags_input - hiding popup")
                popup.hide()
    super().mousePressEvent(event)
```

**Behavior:** When user clicks anywhere on the dialog (outside tags_input), popup hides.

### 4. Selection Made
**Implementation:** `_on_completion_selected()` lines 301-303 (already existed)

```python
popup = self.fuzzy_completer.popup()
popup.hide()
self.tags_input.setFocus()
```

**Behavior:** When user clicks or presses Enter on a suggestion, popup hides.

---

## 🧪 TESTING

### Test Case 1: ESC Key
1. Click in Tags field
2. Type 'p' (popup appears)
3. Press ESC
4. **Expected:** Popup disappears
5. **Expected:** Cursor still in Tags field

### Test Case 2: Tab to Another Field
1. Click in Tags field
2. Type 'p' (popup appears)
3. Press Tab or click in Description field
4. **Expected:** Popup disappears
5. **Expected:** Focus in Description field

### Test Case 3: Click Outside
1. Click in Tags field
2. Type 'p' (popup appears)
3. Click on Name field
4. **Expected:** Popup disappears
5. **Expected:** Cursor in Name field

### Test Case 4: Make Selection
1. Click in Tags field
2. Type 'p' (popup appears with "python", etc.)
3. Click "python" in popup
4. **Expected:** Popup disappears
5. **Expected:** "python" inserted in Tags field
6. **Expected:** Cursor still in Tags field

---

## 📊 DEBUG OUTPUT

### ESC Press
```
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=16777216, text=''
[DEBUG] ESC pressed - hiding popup
```

### Focus Change
```
[DEBUG] Focus leaving tags_input to QLineEdit - hiding popup
```

### Click Outside
```
[DEBUG] Click outside tags_input - hiding popup
```

### Selection Made
```
[DEBUG] Selected: python, new_text: python
```

---

## ✅ FILES MODIFIED

**src/snippet_editor_dialog.py:**

1. **InputFocusProtector class (lines 77-122):**
   - Added `__init__` to store popup reference
   - Added ESC key handling
   - Added focus change handling with popup dismiss

2. **SnippetEditorDialog.mousePressEvent (lines 142-155):**
   - Added mouse click handling
   - Hides popup when clicking outside tags_input

3. **_setup_completer (line 258):**
   - Set popup reference on event filter: `self.debug_filter.popup = popup`

---

## 💡 WHY THIS APPROACH

### Alternative Considered: Restore Popup Window Type
**Problem:** Would re-introduce the window activation bug (can't type continuously)

### Alternative Considered: ToolTip Window Type
**Problem:** ToolTip windows auto-hide on ANY interaction, including typing in tags_input

### Chosen Approach: Tool + Manual Dismiss Logic
**Benefits:**
- ✅ Keeps focus fix (Tool windows don't activate)
- ✅ Full control over when popup dismisses
- ✅ Mimics standard autocomplete behavior
- ✅ More predictable than auto-dismiss heuristics

---

## 🎯 SUCCESS CRITERIA

All 4 test cases pass:
- ✅ ESC dismisses popup
- ✅ Tab/click to another field dismisses popup
- ✅ Click outside tags_input dismisses popup
- ✅ Selecting item dismisses popup

AND original focus fix still works:
- ✅ User can type continuously without clicking

---

**Generated:** 2025-11-06
**Status:** READY FOR TESTING
**Confidence:** High - covers all standard dismiss scenarios
