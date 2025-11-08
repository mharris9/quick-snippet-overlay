# HANDOFF: Add "New Snippet" Button to Main Overlay

**Project:** Quick Snippet Overlay
**Feature:** Easy access to Add Snippet dialog from main overlay
**Priority:** Enhancement - User Experience Improvement
**Date:** 2025-11-06
**Current Status:** Phase 5 Complete - Ready for Phase 6 enhancements

---

## 🎯 FEATURE REQUEST

### User Goal
Make it easier to add new snippets while using the overlay. Currently requires:
1. Right-click system tray icon
2. Click "Add Snippet"

**Desired:** Add snippet creation in **1-2 clicks from the overlay itself**.

### User Quote
> "I want to make it easier to open the Add Snippet window from the main overlay. I want to do this in one or maximum two clicks. Can we add a menu to the overlay to access Add Snippet easier?"

---

## 📋 CURRENT STATE

### Project Status
- **Phase 5**: Tag Autocomplete - ✅ COMPLETE (just pushed to GitHub)
- **Commit**: `bad1170` on master branch
- **Repository**: https://github.com/mharris9/quick-snippet-overlay
- **Tests**: 124/128 passing (97%)
- **Coverage**: 83%

### Main Overlay Current Functionality
**File:** `src/overlay_window.py`

**Current Features:**
- Frameless, always-on-top Qt window
- Search input field for filtering snippets
- Results list showing matching snippets
- Keyboard navigation (arrows, Enter, ESC)
- Double-click or Enter to select snippet
- ESC to close overlay

**Current UI Layout:**
```
┌─────────────────────────────────┐
│  [Search input field]           │ ← QLineEdit
├─────────────────────────────────┤
│  Snippet 1 name                 │ ← QListWidget
│  Snippet 2 name                 │
│  Snippet 3 name                 │
│  ...                            │
└─────────────────────────────────┘
```

**Key Code Sections:**
- `_setup_ui()`: Creates layout (lines ~50-120)
- `search_input`: QLineEdit for search
- `results_list`: QListWidget for results
- Window shows centered on active monitor
- Hides 500ms after snippet selection

---

## 💡 DESIGN CONSIDERATIONS

### Option 1: Add Button in Overlay (RECOMMENDED)
Add a "+ New Snippet" button to the overlay interface.

**Placement Options:**
1. **Top-right corner** (next to search field)
2. **Bottom of overlay** (below results list)
3. **Toolbar above search** (dedicated button row)

**Mockup (Top-right placement):**
```
┌─────────────────────────────────┐
│  [Search input field]     [+ ]  │ ← Button here
├─────────────────────────────────┤
│  Snippet 1 name                 │
│  Snippet 2 name                 │
│  Snippet 3 name                 │
│  ...                            │
└─────────────────────────────────┘
```

**Pros:**
- Always visible when overlay is open
- Single click to add snippet
- Intuitive placement
- No extra keypress needed

**Cons:**
- Takes up screen space
- Requires UI layout changes

### Option 2: Context Menu on Right-Click
Add right-click context menu to overlay window.

**Menu Items:**
- "New Snippet"
- "Edit Snippet" (if one is selected)
- "Settings"
- "Quit"

**Pros:**
- No UI space used
- Familiar pattern
- Can add multiple actions

**Cons:**
- Requires right-click (less discoverable)
- 2 clicks instead of 1

### Option 3: Keyboard Shortcut
Add `Ctrl+N` or `Ctrl+Shift+N` shortcut when overlay is focused.

**Pros:**
- Zero visual clutter
- Fast for power users
- Easy to implement

**Cons:**
- Not discoverable
- Requires remembering shortcut

### Option 4: Combination Approach (BEST USER EXPERIENCE)
Implement **Option 1 (button) + Option 3 (shortcut)**:
- Visual button for discoverability
- Keyboard shortcut for power users
- Both trigger the same action

---

## 🔧 TECHNICAL IMPLEMENTATION

### Recommended Approach: Button + Shortcut

#### 1. Add Button to Overlay
**File:** `src/overlay_window.py`

**Changes to `_setup_ui()`:**
```python
# Add button to top layout (horizontal layout)
top_layout = QHBoxLayout()
self.search_input = QLineEdit()
self.search_input.setPlaceholderText("Search snippets...")

# Add "New Snippet" button
self.add_button = QPushButton("+")  # or "+ New"
self.add_button.setToolTip("Add New Snippet (Ctrl+N)")
self.add_button.setFixedWidth(40)  # Small button
self.add_button.clicked.connect(self._on_add_snippet_clicked)

top_layout.addWidget(self.search_input)
top_layout.addWidget(self.add_button)

layout.addLayout(top_layout)
```

**Styling:**
```python
# Make button visually distinct but not intrusive
self.add_button.setStyleSheet("""
    QPushButton {
        background-color: #4CAF50;
        color: white;
        border: none;
        border-radius: 4px;
        font-size: 16px;
        font-weight: bold;
    }
    QPushButton:hover {
        background-color: #45a049;
    }
""")
```

#### 2. Add Keyboard Shortcut
**File:** `src/overlay_window.py`

**Override `keyPressEvent()`:**
```python
def keyPressEvent(self, event):
    """Handle keyboard shortcuts."""
    # Ctrl+N to add new snippet
    if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyModifier.ControlModifier:
        self._on_add_snippet_clicked()
        event.accept()
        return

    # Pass other keys to parent (existing ESC handling, etc.)
    super().keyPressEvent(event)
```

#### 3. Implement Add Snippet Handler
**File:** `src/overlay_window.py`

**Add method:**
```python
def _on_add_snippet_clicked(self):
    """Open the Add Snippet dialog."""
    from src.snippet_editor_dialog import SnippetEditorDialog

    # Create and show dialog
    dialog = SnippetEditorDialog(
        snippet_manager=self.snippet_manager,
        parent=self  # Overlay as parent for proper stacking
    )

    # Show dialog modally
    result = dialog.exec()

    # If snippet was saved, refresh the overlay results
    if result == QDialog.DialogCode.Accepted:
        # Reload snippets (snippet_manager watches file, but force refresh)
        self._update_results(self.search_input.text())

        # Optionally: Show success message
        # QMessageBox.information(self, "Success", "Snippet added!")
```

#### 4. Wire to SystemTray (Optional)
If you want consistency, the system tray's "Add Snippet" should call the same handler:

**File:** `src/system_tray.py`

**Modify `_create_add_snippet_action()`:**
```python
def _create_add_snippet_action(self):
    """Create Add Snippet action."""
    add_action = QAction("Add Snippet", self)
    add_action.triggered.connect(self._on_add_snippet)
    return add_action

def _on_add_snippet(self):
    """Open Add Snippet dialog."""
    from src.snippet_editor_dialog import SnippetEditorDialog

    dialog = SnippetEditorDialog(snippet_manager=self.snippet_manager)
    dialog.exec()
```

---

## 🧪 TESTING REQUIREMENTS

### Manual Testing

**Test Case 1: Button Click**
1. Press `Ctrl+Shift+Space` to open overlay
2. Click the "+ New" button in top-right
3. **Expected:** Add Snippet dialog opens
4. Fill in snippet details and save
5. **Expected:** Dialog closes, overlay updates with new snippet

**Test Case 2: Keyboard Shortcut**
1. Open overlay
2. Press `Ctrl+N`
3. **Expected:** Add Snippet dialog opens
4. Press ESC to cancel
5. **Expected:** Dialog closes, overlay still open

**Test Case 3: Dialog Stacking**
1. Open overlay
2. Click "+ New" button
3. **Expected:** Dialog appears on top of overlay
4. Save snippet
5. **Expected:** Focus returns to overlay

**Test Case 4: Search Preservation**
1. Open overlay
2. Type "python" in search field
3. Click "+ New" button
4. Cancel dialog
5. **Expected:** Search text "python" still in field

**Test Case 5: Button Styling**
1. Open overlay
2. Hover over "+ New" button
3. **Expected:** Button changes color (hover state)
4. **Expected:** Tooltip shows "Add New Snippet (Ctrl+N)"

### Automated Testing

**File:** `tests/test_overlay_window.py`

**Add tests:**
```python
def test_add_snippet_button_exists(qtbot, mocker):
    """Test that add snippet button is present."""
    overlay = OverlayWindow()
    qtbot.addWidget(overlay)
    overlay.show()

    assert hasattr(overlay, 'add_button')
    assert overlay.add_button.text() in ["+", "+ New", "New Snippet"]

def test_add_snippet_button_click_opens_dialog(qtbot, mocker):
    """Test clicking add button opens dialog."""
    mock_dialog = mocker.patch('src.overlay_window.SnippetEditorDialog')

    overlay = OverlayWindow()
    qtbot.addWidget(overlay)
    overlay.show()

    # Click button
    qtbot.mouseClick(overlay.add_button, Qt.MouseButton.LeftButton)

    # Verify dialog was created and shown
    mock_dialog.assert_called_once()
    mock_dialog.return_value.exec.assert_called_once()

def test_ctrl_n_shortcut_opens_dialog(qtbot, mocker):
    """Test Ctrl+N keyboard shortcut."""
    mock_dialog = mocker.patch('src.overlay_window.SnippetEditorDialog')

    overlay = OverlayWindow()
    qtbot.addWidget(overlay)
    overlay.show()

    # Press Ctrl+N
    qtbot.keyPress(overlay, Qt.Key.Key_N, Qt.KeyModifier.ControlModifier)

    # Verify dialog opened
    mock_dialog.assert_called_once()
```

---

## 🎨 UI/UX POLISH

### Button Design Options

**Option A: Icon Button (Minimalist)**
```python
self.add_button = QPushButton("+")
self.add_button.setFixedSize(30, 30)
```
- Pros: Small, unobtrusive
- Cons: Less obvious what it does

**Option B: Text Button**
```python
self.add_button = QPushButton("+ New")
self.add_button.setFixedWidth(80)
```
- Pros: Clear purpose
- Cons: Takes more space

**Option C: Icon + Tooltip (RECOMMENDED)**
```python
self.add_button = QPushButton("+")
self.add_button.setToolTip("Add New Snippet (Ctrl+N)")
self.add_button.setFixedSize(40, 30)
```
- Pros: Compact, discoverable via tooltip
- Cons: Requires hover to see full info

### Color Scheme
Match existing dark theme:
- Background: Green (#4CAF50) for "add" action
- Hover: Slightly darker green (#45a049)
- Text: White for contrast
- Border: None (modern flat design)

### Accessibility
- Tooltip for screen readers
- Keyboard shortcut for keyboard-only users
- High contrast colors
- Focus indicator when tabbing

---

## 📁 FILES TO MODIFY

### Primary
1. **src/overlay_window.py** (main changes)
   - `_setup_ui()`: Add button to layout
   - `keyPressEvent()`: Add Ctrl+N shortcut
   - `_on_add_snippet_clicked()`: New method for handling action

### Secondary (Optional)
2. **src/system_tray.py**
   - Refactor "Add Snippet" action to reuse same handler
   - Consistency between tray and overlay

3. **tests/test_overlay_window.py**
   - Add tests for button existence
   - Add tests for button click
   - Add tests for Ctrl+N shortcut

### Documentation
4. **CLAUDE.md**
   - Update overlay features list
   - Document keyboard shortcut

---

## ⚠️ POTENTIAL ISSUES & SOLUTIONS

### Issue 1: Dialog Parenting
**Problem:** If dialog parent is not set correctly, it may appear behind overlay or on wrong monitor.

**Solution:**
```python
dialog = SnippetEditorDialog(
    snippet_manager=self.snippet_manager,
    parent=self  # Set overlay as parent
)
```

### Issue 2: Overlay Focus After Dialog
**Problem:** After closing dialog, focus might not return to overlay.

**Solution:**
```python
result = dialog.exec()
if result == QDialog.DialogCode.Accepted:
    self._update_results(self.search_input.text())
    self.search_input.setFocus()  # Restore focus to search
```

### Issue 3: Button Size on Small Windows
**Problem:** Button might be too large on minimum overlay size.

**Solution:**
```python
# Use fixed width, not percentage
self.add_button.setFixedWidth(40)
# Or make it scale
self.add_button.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Preferred)
```

### Issue 4: Keyboard Shortcut Conflicts
**Problem:** Ctrl+N might conflict with existing shortcuts.

**Solution:**
- Check if Ctrl+N is used elsewhere (it's not currently)
- Document in tooltip and user guide
- Make configurable in settings (future enhancement)

---

## 🎯 SUCCESS CRITERIA

### Must Have
- ✅ "+ New" button visible in overlay
- ✅ Single click opens Add Snippet dialog
- ✅ Ctrl+N keyboard shortcut works
- ✅ Dialog appears on top of overlay
- ✅ Overlay refreshes after saving new snippet
- ✅ Search text preserved when canceling dialog

### Nice to Have
- ✅ Button has hover effect
- ✅ Tooltip shows keyboard shortcut
- ✅ Focus returns to search field after dialog
- ✅ Tests cover button and shortcut
- ✅ Consistent with system tray action

### Polish
- ✅ Button matches dark theme
- ✅ Smooth transitions
- ✅ Accessible (screen readers, keyboard-only)

---

## 📊 ESTIMATED EFFORT

**Time:** 1-2 hours
**Complexity:** Low-Medium
**Risk:** Low (isolated feature, doesn't affect existing functionality)

**Breakdown:**
- UI layout changes: 30 min
- Add snippet handler: 15 min
- Keyboard shortcut: 15 min
- Styling: 15 min
- Testing: 30 min
- Documentation: 15 min

---

## 🔮 FUTURE ENHANCEMENTS

### Phase 1 (This Session)
- Add button to overlay
- Implement Ctrl+N shortcut
- Basic testing

### Phase 2 (Future)
- Right-click context menu with "New Snippet", "Edit", "Delete"
- Inline snippet editing (edit selected snippet with Ctrl+E)
- Quick add from clipboard (Ctrl+Shift+V)

### Phase 3 (Future)
- Customizable keyboard shortcuts in settings
- Button position configurable (top/bottom/left/right)
- Icon library for button (use actual icon instead of "+")

---

## 📝 HANDOFF CHECKLIST

Before starting:
- [ ] Read this document fully
- [ ] Understand current overlay structure (`src/overlay_window.py`)
- [ ] Review SnippetEditorDialog API (`src/snippet_editor_dialog.py`)
- [ ] Check existing tests (`tests/test_overlay_window.py`)

During implementation:
- [ ] Add button to overlay UI
- [ ] Implement Ctrl+N shortcut
- [ ] Create `_on_add_snippet_clicked()` handler
- [ ] Test button click manually
- [ ] Test keyboard shortcut manually
- [ ] Add automated tests

After implementation:
- [ ] Run all tests (`pytest`)
- [ ] Format code (`black src/ tests/`)
- [ ] Update CLAUDE.md
- [ ] Create commit with clear message
- [ ] Push to GitHub

---

## 🚀 QUICKSTART

**To implement this feature:**

1. **Open overlay file:**
   ```
   src/overlay_window.py
   ```

2. **Add button in `_setup_ui()`** (around line 60-80):
   ```python
   # Create horizontal layout for search + button
   top_layout = QHBoxLayout()
   top_layout.addWidget(self.search_input)

   self.add_button = QPushButton("+")
   self.add_button.setToolTip("Add New Snippet (Ctrl+N)")
   self.add_button.setFixedSize(40, 30)
   self.add_button.clicked.connect(self._on_add_snippet_clicked)
   top_layout.addWidget(self.add_button)

   layout.addLayout(top_layout)
   ```

3. **Add handler method:**
   ```python
   def _on_add_snippet_clicked(self):
       """Open Add Snippet dialog."""
       from src.snippet_editor_dialog import SnippetEditorDialog
       dialog = SnippetEditorDialog(snippet_manager=self.snippet_manager, parent=self)
       result = dialog.exec()
       if result == QDialog.DialogCode.Accepted:
           self._update_results(self.search_input.text())
           self.search_input.setFocus()
   ```

4. **Add keyboard shortcut:**
   ```python
   def keyPressEvent(self, event):
       if event.key() == Qt.Key.Key_N and event.modifiers() == Qt.KeyModifier.ControlModifier:
           self._on_add_snippet_clicked()
           event.accept()
           return
       super().keyPressEvent(event)
   ```

5. **Test manually:**
   - Run app: `RUN-APP.bat`
   - Open overlay: Ctrl+Shift+Space
   - Click button: Should open dialog
   - Try Ctrl+N: Should open dialog

6. **Commit and push:**
   ```bash
   git add .
   git commit -m "Add '+ New' button and Ctrl+N shortcut to overlay"
   git push origin master
   ```

---

**Generated:** 2025-11-06
**For:** Phase 6 - Overlay Enhancement
**Status:** READY TO IMPLEMENT
**Difficulty:** Easy 🟢
**Impact:** High (improves user workflow significantly)

