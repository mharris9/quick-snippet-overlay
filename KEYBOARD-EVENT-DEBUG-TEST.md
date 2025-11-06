# Keyboard Event Routing Debug - Test #4

**Date:** 2025-11-06
**Issue:** Focus shows QLineEdit but user still can't type continuously
**Theory:** Keyboard events are being routed to popup despite focus being on tags_input

---

## 🔍 THE MYSTERY

From your previous test, the debug log showed:
- ✅ Focus ALWAYS on QLineEdit (never changed to NoFocusListView)
- ✅ You typed 'p' then 'py' (two separate calls)
- ❌ You still report "same issue" - can't type continuously

**This suggests:** Qt's focus widget is correct, but **keyboard events** are going somewhere else!

---

## 🆕 NEW DEBUGGING ADDED

### 1. Keyboard Event Tracking in tags_input
**Location:** `InputFocusProtector.eventFilter()` lines 83-88

Will print:
```
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=80, text='p'
```

### 2. Keyboard Event Tracking in popup
**Location:** `NoFocusListView.keyPressEvent()` lines 48-55

Will print:
```
[KEYBOARD DEBUG] NoFocusListView received key: 80 - REJECTING and ignoring
```

### 3. General Event Tracking in popup
**Location:** `NoFocusListView.event()` lines 57-66

Will print:
```
[EVENT DEBUG] NoFocusListView.event() received: KeyPress - IGNORING
```

### 4. Popup Rejects ALL Keyboard Events
The popup now explicitly rejects all keyboard events and doesn't call super(), which should prevent it from handling ANY keys.

---

## 🧪 TESTING PROCEDURE

### Step 1: Launch Application
```powershell
RUN-APP.bat
```

### Step 2: Open Add Snippet Dialog
1. Right-click system tray icon
2. Click "Add Snippet"
3. Click in Tags field

### Step 3: Type ONE Letter
Type: **p** (just the letter 'p')

### Step 4: Analyze Debug Output

**SCENARIO A: Normal Behavior (what we expect)**
```
[DEBUG] Event filter installed on tags_input for keyboard debugging
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=80, text='p'
[FOCUS DEBUG] === _on_tags_input_changed() START ===
[FOCUS DEBUG] Focus on: QLineEdit
...
```
Keyboard goes to tags_input → Focus stays on QLineEdit → Everything works ✅

**SCENARIO B: Popup Stealing Events (the bug we suspect)**
```
[DEBUG] Event filter installed on tags_input for keyboard debugging
[EVENT DEBUG] NoFocusListView.event() received: KeyPress - IGNORING
[KEYBOARD DEBUG] NoFocusListView received key: 80 - REJECTING and ignoring
```
Keyboard goes to popup FIRST → tags_input never gets it → Bug confirmed ❌

**SCENARIO C: Both Receive Events (event propagation issue)**
```
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=80, text='p'
[EVENT DEBUG] NoFocusListView.event() received: KeyPress - IGNORING
[KEYBOARD DEBUG] NoFocusListView received key: 80 - REJECTING and ignoring
[FOCUS DEBUG] === _on_tags_input_changed() START ===
```
Event goes to BOTH widgets → This is wrong but at least tags_input gets it

---

## 🎯 CRITICAL QUESTIONS TO ANSWER

### Question 1: Where do keyboard events go FIRST?

Look at the FIRST debug line after you type 'p':

- ✅ `[KEYBOARD DEBUG] tags_input RECEIVED...` → Events go to tags_input (correct)
- ❌ `[EVENT DEBUG] NoFocusListView.event()...` → Events go to popup (BUG!)

### Question 2: Does tags_input receive the event AT ALL?

Search the output for:
```
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress
```

- ✅ Found → tags_input gets keyboard events
- ❌ Not found → tags_input is NOT receiving keyboard events (BUG!)

### Question 3: Does the popup receive keyboard events?

Search the output for:
```
[EVENT DEBUG] NoFocusListView.event() received: KeyPress
```

- ✅ Found → Popup is intercepting keyboard events (BUG!)
- ❌ Not found → Popup correctly ignores keyboard events

---

## 📊 EXPECTED vs ACTUAL

### EXPECTED Debug Output (if working correctly):
```
[DEBUG] Event filter installed on tags_input for keyboard debugging

[User types 'p']
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=80, text='p'

[FOCUS DEBUG] === _on_tags_input_changed() START ===
[FOCUS DEBUG] Focus on: QLineEdit
[FOCUS DEBUG] Text: 'p'
[DEBUG] current_tag='p', matches=[...]
...

[User types 'y']
[KEYBOARD DEBUG] tags_input RECEIVED KeyPress: key=89, text='y'

[FOCUS DEBUG] === _on_tags_input_changed() START ===
[FOCUS DEBUG] Focus on: QLineEdit
[FOCUS DEBUG] Text: 'py'
```

Notice: NO messages from NoFocusListView about keyboard events!

### ACTUAL Debug Output (if bug exists):
```
[DEBUG] Event filter installed on tags_input for keyboard debugging

[User types 'p']
[EVENT DEBUG] NoFocusListView.event() received: QEvent.Type.KeyPress - IGNORING
[KEYBOARD DEBUG] NoFocusListView received key: 80 - REJECTING and ignoring
(Possibly followed by tags_input receiving it, or not)
```

Notice: Popup receives keyboard event FIRST (or ONLY)!

---

## 🔧 WHAT THIS TEST WILL REVEAL

### If Popup Receives Keyboard Events:
**Root Cause:** Qt is routing keyboard events to the popup window despite:
- NoFocus policy
- WA_ShowWithoutActivating attribute
- Focus widget being QLineEdit

**Solution:** Make popup reject keyboard events even more aggressively:
- Override `event()` to block ALL keyboard events (already done in this test)
- Possibly need to set `Qt.WindowType.ToolTip` instead of `Popup`
- May need to use `setAttribute(Qt.WA_TransparentForMouseEvents)` for keyboard too

### If tags_input Receives Events But User Still Can't Type:
**Root Cause:** Something else is consuming the text AFTER the event is processed

**Solution:** Check if:
- The text is being cleared somewhere
- Selection is being changed (cursor moved to start/end)
- Another event filter is blocking text insertion

### If BOTH Receive Events:
**Root Cause:** Event propagation is sending events to multiple widgets

**Solution:** Make tags_input event filter block propagation:
```python
if event.type() == QEvent.Type.KeyPress:
    event.accept()  # Stop propagation
    return False  # Let tags_input handle it
```

---

## 🚀 ACTION PLAN

1. **Run test** - Type 'p' in Tags field
2. **Copy full debug output** - From app start to after typing 'p'
3. **Analyze event routing** - Who gets keyboard events first/only?
4. **Report findings** - Paste debug output and describe user experience

---

## 💡 THE FIX (if popup is stealing events)

The code changes in this test already include the fix:
- `NoFocusListView.keyPressEvent()` rejects all keys with `event.ignore()`
- `NoFocusListView.event()` returns `False` for all keyboard events
- This should prevent the popup from "eating" the keyboard input

**If this works**, you should be able to type continuously now!

---

## ✅ SUCCESS CRITERIA

After this test, you should be able to type "python" continuously without clicking, AND we'll understand exactly why the previous fixes didn't work.

---

**Generated:** 2025-11-06
**Test Type:** Keyboard Event Routing Diagnosis
**Expected Time:** 2 minutes
