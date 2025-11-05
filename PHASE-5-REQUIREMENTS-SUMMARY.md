# Phase 5 Requirements Summary

## Overlay Window Specifications
- **Dimensions**: 600x400px (configurable)
- **Position**: Centered on ACTIVE monitor (multi-monitor support)
- **Fallback**: Primary monitor if active detection fails
- **Style**: 
  - Frameless (no title bar)
  - Always-on-top
  - 95% opacity (semi-transparent)
  - 10px rounded corners
  - Dark theme default

## Search Functionality
- **Real-time updates**: Results update as user types
- **Debouncing**: 150ms delay (configurable)
- **Empty search**: Show no results
- **Integration**: Calls SearchEngine.search() with query

## Keyboard Navigation
- **Arrow Down**: Navigate to next result
- **Arrow Up**: Navigate to previous result
- **Enter**: Copy selected snippet (with variable substitution if needed)
- **ESC**: Close overlay

## Variable Prompt Dialog
- **Modal dialog**: 400x150px, centered on overlay
- **Sequential prompts**: One dialog per variable in order
- **Label**: "Enter value for: {variable_name}"
- **Input field**: Pre-populated with default value if specified
- **Validation**: Require non-empty input, show error if empty
- **Cancel behavior**: Abort entire copy operation, keep overlay open
- **OK behavior**: Accept value, proceed to next variable or complete

## Visual Feedback
- **"Copied!" message**: Green, bold, center-aligned
- **Duration**: Show for 500ms, then hide
- **Auto-close**: Overlay closes 500ms after copy (after feedback shown)

## Multi-Monitor Support
- **Detection**: QCursor.pos() + QApplication.screenAt()
- **Centering**: Calculate center relative to active screen geometry
- **Formula**: x = screen.x() + (screen.width() - overlay.width()) // 2

## Results Display
- **Truncation**: Show first 2 lines of snippet content with "..." indicator
- **Format**: Snippet name (bold, 14pt) + truncated content (11pt)
- **Selection**: Accent color background for selected item
- **Scrollable**: List scrolls if >10 results

## Integration Points
- **SnippetManager**: Load snippets, access snippet list
- **SearchEngine**: Fuzzy search with query, thresholds
- **VariableHandler**: detect_variables(), substitute_variables()
- **ConfigManager**: Read overlay dimensions, opacity, theme, debounce

## Success Criteria
- 13 tests for overlay_window.py
- 7 tests for variable_prompt_dialog.py
- 95%+ test pass rate (UI tests can be flaky)
- ≥90% coverage for both files
- All Phase 1-4 tests still passing (58/58)
