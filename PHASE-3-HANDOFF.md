# Phase 3 Handoff: Variable Handler Implementation

## Session Header

**Project**: Quick Snippet Overlay - Windows 11 Hotkey-Activated Text Snippet Tool
**Phase**: Phase 3 of 7 - Variable Handler Implementation
**Status**: Phase 1  COMPLETE | Phase 2  COMPLETE | Phase 3 = READY TO START
**Session Type**: Feature Development (TDD Methodology)
**Working Directory**: `C:\Users\mikeh\software_projects\quick-snippet-overlay`
**Duration Estimate**: 1.5-2 hours

---

## Quick Start Command

```powershell
# Verify environment and start Phase 3
cd C:\Users\mikeh\software_projects\quick-snippet-overlay
python -m pytest tests/test_variable_handler.py -v --cov=src.variable_handler --cov-report=term-missing
```

**First Action**: Invoke the `workflow-coordinator` subagent to orchestrate the 9-step TDD workflow for Phase 3.

---

## Phase 3 Objectives

**Goal**: Implement robust variable detection and substitution for snippet content.

**Component**: `src/variable_handler.py`

**Core Functionality**:
1. **Detect variables** in snippet content using patterns: `{{variable_name}}` or `{{variable_name:default_value}}`
2. **Parse variable metadata**: Extract variable names, default values, and positions
3. **Handle edge cases**: Multiple occurrences of same variable, invalid names, nested braces
4. **Validate variable names**: Alphanumeric characters and underscores only
5. **Perform substitution**: Replace variables with user-provided or default values

**Key Requirements from PRD Section 5.1.1**:
- Support both `{{var}}` and `{{var:default}}` syntax
- Single prompt per variable (even if used multiple times)
- Substitute ALL occurrences of a variable with the same value
- Reject invalid variable names (empty, special characters except underscore)
- Treat nested braces as literals when malformed

---

## Previous Phase Completion Summary

### Phase 1: Snippet Manager  COMPLETE
- **File**: `src/snippet_manager.py`
- **Status**: 19/19 tests passing, 94% coverage
- **Features**: YAML loading, validation, file watching, backup management, hot-reloading
- **Report**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\PHASE-1-COMPLETION-REPORT.md`

### Phase 2: Search Engine  COMPLETE
- **File**: `src/search_engine.py`
- **Status**: 12/12 tests passing, 98% coverage
- **Features**: Fuzzy search with typo tolerance, weighted scoring (name=3x, tags=2x, content=1x)
- **Performance**: 166x faster than target (1,660 searches/sec vs 10/sec target)
- **Report**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\PHASE-2-COMPLETION-REPORT.md`

---

## 9-Step TDD Workflow for Phase 3

**CRITICAL**: Follow TDD methodology strictly - **WRITE TESTS FIRST**, then implement.

### Step 1: Review Phase 3 Requirements (15 min)
**Action**: Read PRD Section 5.1.1 (Variable Substitution) and Implementation Plan Phase 3 section.

**Key Documents**:
- PRD: `C:\Users\mikeh\software_projects\brainstorming\PRD-quick-snippet-overlay-v2.md` (Section 5.1.1)
- Implementation Plan: `C:\Users\mikeh\software_projects\brainstorming\PHASED-IMPLEMENTATION-PLAN-v2.md` (Lines 617-668)

**Output**: Document understanding of:
- Variable syntax patterns
- Edge cases (nested braces, invalid names, duplicates)
- Expected behavior for substitution

**Todo Item**: "Review Phase 3 requirements from PRD and Implementation Plan"

---

### Step 2: Create Test File Structure (10 min)
**Action**: Create `tests/test_variable_handler.py` with 10 test function stubs.

**Required Test Functions**:
1. `test_no_variables` - Content with no variables returns empty list
2. `test_simple_variable` - Detect `{{var}}`
3. `test_variable_with_default` - Detect `{{var:default}}`
4. `test_multiple_variables` - Detect multiple distinct variables
5. `test_duplicate_variable` - Same variable appears multiple times (return once)
6. `test_invalid_variable_names` - Reject empty names, special characters
7. `test_nested_braces_literal` - `{{{var}}}` or `{{}}` treated as literals
8. `test_empty_variable_name` - `{{}}` or `{{:default}}` rejected
9. `test_substitute_variables` - Replace variables with provided values
10. `test_substitute_multiple_occurrences` - Same variable used twice, both replaced

**File Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\tests\test_variable_handler.py`

**Todo Item**: "Create test file with 10 test function stubs"

---

### Step 3: Write Detection Tests (20 min)
**Action**: Implement tests 1-8 (detection and validation) with assertions.

**Test Pattern**:
```python
def test_simple_variable():
    content = "Run {{command}} on server"
    variables = detect_variables(content)
    assert len(variables) == 1
    assert variables[0]['name'] == 'command'
    assert variables[0]['default'] is None
```

**Run Tests**:
```powershell
python -m pytest tests/test_variable_handler.py::test_simple_variable -v
```

**Expected Result**: All tests FAIL (no implementation yet - this is correct TDD).

**Todo Item**: "Write detection and validation tests (tests 1-8)"

---

### Step 4: Implement Detection Logic (25 min)
**Action**: Create `src/variable_handler.py` with `detect_variables()` function.

**Requirements**:
- Use regex to find `{{...}}` patterns
- Parse variable name and optional default value (split on `:`)
- Validate variable names: `^[a-zA-Z0-9_]+$`
- Return list of dicts: `[{'name': str, 'default': str|None}, ...]`
- Deduplicate: If `{{var}}` appears 3 times, return once

**File Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\src\variable_handler.py`

**Run Tests**:
```powershell
python -m pytest tests/test_variable_handler.py -k "not substitute" -v
```

**Expected Result**: Tests 1-8 PASS.

**Todo Item**: "Implement detect_variables() function and pass tests 1-8"

---

### Step 5: Write Substitution Tests (15 min)
**Action**: Implement tests 9-10 (substitution logic) with assertions.

**Test Pattern**:
```python
def test_substitute_variables():
    content = "Hello {{name}}, welcome to {{place:Earth}}"
    values = {'name': 'Alice', 'place': 'Mars'}
    result = substitute_variables(content, values)
    assert result == "Hello Alice, welcome to Mars"
```

**Run Tests**:
```powershell
python -m pytest tests/test_variable_handler.py::test_substitute_variables -v
```

**Expected Result**: Tests FAIL (no substitution implementation yet).

**Todo Item**: "Write substitution tests (tests 9-10)"

---

### Step 6: Implement Substitution Logic (20 min)
**Action**: Add `substitute_variables()` function to `src/variable_handler.py`.

**Requirements**:
- Accept `content: str` and `values: dict[str, str]`
- Replace ALL occurrences of `{{var}}` or `{{var:default}}` with provided value
- Use default value if variable not in `values` dict
- Preserve content unchanged if variable has no value and no default

**Run Tests**:
```powershell
python -m pytest tests/test_variable_handler.py -v
```

**Expected Result**: ALL 10 tests PASS.

**Todo Item**: "Implement substitute_variables() function and pass tests 9-10"

---

### Step 7: Verify Coverage (10 min)
**Action**: Run coverage report and identify untested code paths.

**Command**:
```powershell
python -m pytest tests/test_variable_handler.py --cov=src.variable_handler --cov-report=term-missing --cov-report=html
```

**Target**: e95% coverage for `src/variable_handler.py`

**If Coverage < 95%**: Add targeted tests for uncovered lines (refer to `htmlcov/index.html`).

**Todo Item**: "Run coverage report and achieve e95% coverage"

---

### Step 8: Edge Case Verification (15 min)
**Action**: Manually test edge cases from PRD Section 5.1.1.

**Test Cases**:
1. **Nested braces**: `"{{{var}}}"` ’ Should NOT detect variable
2. **Empty variable**: `"{{}}"` ’ Should reject
3. **Special characters**: `"{{my-var}}"` ’ Should reject
4. **Underscore allowed**: `"{{my_var}}"` ’ Should detect
5. **Colon in default**: `"{{url:https://example.com}}"` ’ Should parse correctly
6. **Multiple colons**: `"{{time:12:30:45}}"` ’ Should use `"12:30:45"` as default
7. **Whitespace**: `"{{ var }}"` ’ PRD doesn't specify, decide behavior and document

**Document Decisions**: Note any ambiguous cases and chosen behavior in code comments.

**Todo Item**: "Verify edge cases from PRD Section 5.1.1"

---

### Step 9: Create Phase 3 Completion Report (20 min)
**Action**: Document Phase 3 completion following Phase 1/2 report format.

**Report Sections**:
1. **Executive Summary** - Phase 3 status, test results, coverage
2. **Implementation Details** - Key functions, algorithms, design decisions
3. **Test Results** - 10/10 tests passing, coverage percentage
4. **Edge Cases Handled** - List with examples
5. **Performance Notes** - Any performance considerations
6. **Integration Points** - How this connects to overlay UI (Phase 4)
7. **Lessons Learned** - What went well, what was challenging
8. **Next Steps** - Phase 4 preview (Overlay Window)

**File Location**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\PHASE-3-COMPLETION-REPORT.md`

**Todo Item**: "Create Phase 3 Completion Report"

---

## Subagent Delegation Strategy

### Primary Orchestrator: `workflow-coordinator`
**When**: Invoke IMMEDIATELY at session start.

**Purpose**:
- Orchestrate all 9 steps of the TDD workflow
- Manage `TodoWrite` tool to track progress
- Ensure tests are written BEFORE implementation
- Verify each step's completion criteria before proceeding

**Invocation**:
```
Use the workflow-coordinator subagent to execute the 9-step TDD workflow for Phase 3 Variable Handler implementation.
```

### Code Specialist: `code-specialist`
**When**: Stuck on implementation >2 hours OR complex regex/parsing challenges.

**Purpose**:
- Debug failing tests
- Optimize regex patterns for variable detection
- Resolve edge case handling (nested braces, multiple colons)

**Invocation Trigger**:
- Tests 1-8 not passing after 30 minutes of implementation
- Substitution logic failing for edge cases
- Coverage target not met after adding tests

### Final Reviewer: `constructive-critic`
**When**: All tests passing, ready to create completion report.

**Purpose**:
- Review code quality and adherence to PRD
- Verify edge case coverage
- Check integration readiness for Phase 4
- Validate completion report accuracy

**Invocation Trigger**:
- All 10 tests passing
- Coverage e95%
- Ready to finalize Phase 3

---

## Success Criteria Checklist

Phase 3 is COMPLETE when ALL items are checked:

### Functional Requirements
- [ ] `src/variable_handler.py` created with `detect_variables()` and `substitute_variables()` functions
- [ ] Detects `{{var}}` syntax correctly
- [ ] Detects `{{var:default}}` syntax correctly
- [ ] Parses variable names and default values
- [ ] Validates variable names (alphanumeric + underscore only)
- [ ] Handles multiple distinct variables in one snippet
- [ ] Deduplicates repeated variables (returns each variable once)
- [ ] Substitutes ALL occurrences of a variable with same value
- [ ] Uses default values when variable value not provided
- [ ] Rejects invalid variable names (empty, special characters)
- [ ] Handles nested braces as literals

### Testing Requirements
- [ ] `tests/test_variable_handler.py` created with 10 test functions
- [ ] All 10 tests passing (100% pass rate)
- [ ] Coverage e95% for `src/variable_handler.py`
- [ ] Edge cases from PRD Section 5.1.1 verified

### Documentation Requirements
- [ ] Code comments explain regex patterns and edge case handling
- [ ] Ambiguous cases documented with chosen behavior
- [ ] `PHASE-3-COMPLETION-REPORT.md` created following Phase 1/2 format

### Integration Readiness
- [ ] API designed for easy integration with overlay UI (Phase 4)
- [ ] Functions return appropriate data structures for prompting user
- [ ] No external dependencies beyond standard library + pytest

---

## Critical Context

### Environment Setup
**Operating System**: Windows 11
**Shell**: PowerShell 7 (use PowerShell commands, NOT bash)
**Python Version**: 3.10+
**Virtual Environment**: Already activated (`.venv`)

**PowerShell Command Examples**:
```powershell
# List files
Get-ChildItem src/

# Search in files
Select-String -Pattern "detect_variables" -Path src/*.py

# Run tests
python -m pytest tests/test_variable_handler.py -v
```

### File Structure
```
C:\Users\mikeh\software_projects\quick-snippet-overlay\
   src\
      __init__.py
      snippet_manager.py       # Phase 1 
      search_engine.py          # Phase 2 
      variable_handler.py       # Phase 3 - TO CREATE
   tests\
      fixtures\
         valid_snippets.yaml
         invalid_snippets.yaml
         search_snippets.yaml
      test_snippet_manager.py
      test_snippet_manager_coverage.py
      test_search_engine.py
      test_variable_handler.py  # Phase 3 - TO CREATE
   requirements.txt
   PHASE-1-COMPLETION-REPORT.md
   PHASE-2-COMPLETION-REPORT.md
```

### Key Commands
```powershell
# Activate virtual environment (if needed)
.\.venv\Scripts\Activate.ps1

# Run all Phase 3 tests
python -m pytest tests/test_variable_handler.py -v

# Run specific test
python -m pytest tests/test_variable_handler.py::test_simple_variable -v

# Run with coverage
python -m pytest tests/test_variable_handler.py --cov=src.variable_handler --cov-report=term-missing --cov-report=html

# Run only detection tests (skip substitution)
python -m pytest tests/test_variable_handler.py -k "not substitute" -v
```

---

## Reference Documents

### Primary References (Absolute Paths)
1. **PRD**: `C:\Users\mikeh\software_projects\brainstorming\PRD-quick-snippet-overlay-v2.md`
   - Section 5.1.1: Variable Substitution (Lines ~350-400)
   - Variable syntax specification
   - Edge case definitions

2. **Implementation Plan**: `C:\Users\mikeh\software_projects\brainstorming\PHASED-IMPLEMENTATION-PLAN-v2.md`
   - Phase 3 Section (Lines 617-668)
   - 9-step TDD workflow
   - Test specifications

3. **Phase 1 Report**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\PHASE-1-COMPLETION-REPORT.md`
   - SnippetManager API reference
   - Testing patterns used

4. **Phase 2 Report**: `C:\Users\mikeh\software_projects\quick-snippet-overlay\PHASE-2-COMPLETION-REPORT.md`
   - SearchEngine API reference
   - Coverage strategies

### Secondary References
5. **Project Spec**: `C:\Users\mikeh\software_projects\brainstorming\quick-snippet-overlay-specification.md`
6. **Sample Snippets**: `C:\Users\mikeh\software_projects\brainstorming\snippets-sample.yaml`
   - Examples of variable usage in real snippets

---

## Design Decisions & Constraints

### Variable Syntax
**Pattern**: `{{variable_name}}` or `{{variable_name:default_value}}`

**Validation Rules**:
- Variable names: `^[a-zA-Z0-9_]+$` (alphanumeric + underscore)
- Empty names rejected: `{{}}` or `{{:default}}`
- Special characters rejected: `{{my-var}}`, `{{my.var}}`

### Edge Case Decisions
1. **Nested Braces**: `{{{var}}}` ’ Treat as literal, do NOT detect variable
2. **Multiple Colons**: `{{time:12:30:45}}` ’ Default value is `"12:30:45"` (everything after first colon)
3. **Whitespace in Braces**: `{{ var }}` ’ **DECISION NEEDED**: Strip whitespace or treat as literal?
4. **Duplicate Variables**: `"{{var}} and {{var}}"` ’ Return variable ONCE, substitute BOTH occurrences

### API Design
```python
def detect_variables(content: str) -> list[dict[str, str|None]]:
    """
    Returns: [
        {'name': 'variable_name', 'default': 'default_value'},
        {'name': 'another_var', 'default': None},
    ]
    """
    pass

def substitute_variables(content: str, values: dict[str, str]) -> str:
    """
    Args:
        content: Original snippet content with variables
        values: {'variable_name': 'user_provided_value', ...}

    Returns: Content with all variables replaced
    """
    pass
```

---

## Gotchas & Common Pitfalls

### 1. Regex Escaping
**Problem**: Braces are special characters in regex.
**Solution**: Escape braces: `r'\{\{([^}]+)\}\}'`

### 2. Greedy vs Non-Greedy Matching
**Problem**: `{{var1}} and {{var2}}` might match as single variable.
**Solution**: Use non-greedy quantifier: `r'\{\{([^}]+?)\}\}'`

### 3. Colon Splitting
**Problem**: `{{url:https://example.com}}` has multiple colons.
**Solution**: Split on FIRST colon only: `name, default = text.split(':', 1)`

### 4. Deduplication Logic
**Problem**: Same variable appears 5 times, but should prompt user ONCE.
**Solution**: Use set or dict to deduplicate by variable name before returning.

### 5. Substitution Order
**Problem**: Substituting `{{var}}` might partially match `{{variable}}`.
**Solution**: Sort variables by length (longest first) OR use regex with word boundaries.

---

## Flow State: Ready to Start

**Current State**: Fresh start, Phase 2 complete, Phase 3 ready to implement.

**Momentum**: High - Phases 1 and 2 completed ahead of schedule with excellent test coverage.

**Blockers**: None - All dependencies in place, environment verified, specifications clear.

**Codebase Health**: STABLE 
- All existing tests passing (31/31)
- No broken functionality
- Clean working directory (all Phase 1/2 files committed)

---

## Next Steps After Phase 3 Completion

### Immediate Actions
1. **Commit Phase 3 work**:
   ```powershell
   git add src/variable_handler.py tests/test_variable_handler.py PHASE-3-COMPLETION-REPORT.md
   git commit -m "Phase 3 complete: Variable handler implementation with 10/10 tests passing"
   ```

2. **Generate Phase 4 handoff prompt** using this same format.

### Phase 4 Preview: Overlay Window (Next Session)
**Component**: `src/overlay_window.py`
**Duration**: 3-4 hours
**Objectives**:
- Create PyQt6 overlay window (frameless, always-on-top)
- Implement center-screen positioning
- Add search input with real-time results display
- Handle keyboard navigation (Arrow keys, Enter, Escape)
- Integrate SnippetManager, SearchEngine, VariableHandler
- Handle variable prompting (use QInputDialog)
- Copy to clipboard on selection

**Test Count**: 15+ tests (UI testing with pytest-qt)

---

## Quality Verification Questions

Before marking Phase 3 complete, verify:

- [ ] Can I copy a snippet with variables end-to-end? (Requires Phase 4 integration)
- [ ] Did I capture WHY certain regex patterns were chosen?
- [ ] Are all edge cases from PRD Section 5.1.1 tested?
- [ ] Would Future Me understand the variable parsing logic 6 months from now?
- [ ] Is the API designed for easy integration with overlay UI?
- [ ] Did I document any ambiguous cases and the chosen behavior?
- [ ] Are file paths in this handoff absolute (not relative)?
- [ ] Is the completion report comprehensive enough to serve as API reference?

---

## Handoff Prompt Summary

This handoff enables a new session to:
1.  Understand project context (Phases 1-2 complete)
2.  Execute Phase 3 using 9-step TDD workflow via `workflow-coordinator` subagent
3.  Follow test-first methodology strictly
4.  Handle all edge cases from PRD
5.  Achieve success criteria (10/10 tests, e95% coverage)
6.  Delegate to `code-specialist` if blocked
7.  Use `constructive-critic` for final review
8.  Create comprehensive completion report
9.  Prepare for Phase 4 integration

**Estimated Time**: 1.5-2 hours (following TDD workflow exactly)

**First Command**: Invoke `workflow-coordinator` subagent to orchestrate the 9-step process.

---

**END OF HANDOFF PROMPT**
