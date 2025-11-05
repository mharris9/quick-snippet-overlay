# Quick Snippet Overlay - Project Instructions for Claude

**Project**: Quick Snippet Overlay - Windows 11 Hotkey-Activated Text Snippet Tool

---

## MANDATORY: Phase Completion Compliance Verification

### ⚠️ CRITICAL REQUIREMENT

**Before writing ANY phase completion report, you MUST:**

1. **Complete Compliance Verification** (Step 13 in every phase)
   - Copy `.claude/PHASE-COMPLIANCE-CHECKLIST.md` to `PHASE-{N}-COMPLIANCE-REVIEW.md`
   - Fill out ALL sections systematically
   - Run verification commands
   - Document ALL discrepancies (P0/P1/P2)
   - Present findings to user

2. **Get User Approval**
   - User must explicitly approve compliance review
   - All P0 critical issues must be resolved OR accepted
   - User chooses: "Compliant, proceed" or "Accepted deviations, proceed"

3. **Only Then Write Completion Report**
   - Include compliance verification section
   - Reference compliance review document
   - Document approved deviations

### Self-Enforcement Protocol

**BEFORE writing completion report, ask yourself:**
- [ ] Does `PHASE-{N}-COMPLIANCE-REVIEW.md` exist?
- [ ] Have I verified technology stack matches PRD?
- [ ] Have I verified all functional requirements implemented?
- [ ] Have I documented ALL discrepancies?
- [ ] Did user approve the compliance review?
- [ ] Are all P0 issues resolved or accepted?

**IF ANY answer is NO → STOP and do compliance verification first**

---

## Phase Completion Workflow

All phases MUST follow this workflow:

1. **Steps 1-12**: Implementation & Testing (phase-specific)
2. **Step 13**: **COMPLIANCE VERIFICATION** (mandatory, 30-45 min)
   - See `.claude/PHASE-COMPLIANCE-CHECKLIST.md`
   - See `.claude/PHASE-COMPLETION-WORKFLOW.md`
3. **Step 14**: Write Completion Report (only after Step 13 approved)
4. **Step 15**: Manual Integration Testing

**ENFORCEMENT**: Refuse to write completion report if Step 13 not completed.

---

## Compliance Verification Process

### What to Verify

**Section 1: Technology Stack**
```bash
# Check PRD specifications
grep -i "technology\|framework\|library" PRD-*.md

# Check actual implementation
grep -r "^from\|^import" src/*.py | sort | uniq

# Compare: Do they match?
```

**Section 2: Functional Requirements**
```bash
# List ALL PRD requirements for this phase
# Verify each is implemented (code + tests)
# Flag any missing or extra features
```

**Section 3-11**: Architecture, integration, config, testing, docs, dependencies, performance, platform

### How to Present Findings

```markdown
## Phase {N} Compliance Review Complete

### ✅ COMPLIANT AREAS
[List what matches PRD/plan]

### ❌ DISCREPANCIES FOUND

**P0 Critical** (Must fix):
1. [Issue: Description, Impact, Options]

**P1 High** (Should fix):
1. [Issue: ...]

**P2 Low** (Document only):
1. [Issue: ...]

### 🤔 DECISION REQUIRED
[Present options A/B/C for each P0/P1 issue]

What should we do?
```

---

## Source of Truth Hierarchy

When documents conflict, priority order:

1. **PRD** (highest authority)
2. **Implementation Plan**
3. **Phase Handoffs**
4. **Existing Code** (lowest - may have bugs/deviations)

**Always check PRD first**, not just existing code.

---

## Technology Standards (Current)

**After Phase 6 Compliance Resolution:**

| Component | Library | Version | License | Status |
|-----------|---------|---------|---------|--------|
| UI Framework | [TBD: PyQt6 or PySide6] | 6.10+ | [TBD: GPL or LGPL] | ⚠️ Under review |
| Search | rapidfuzz | 3.0+ | MIT | ✅ Approved |
| Storage | PyYAML | 6.0+ | MIT | ✅ Approved |
| Clipboard | pyperclip | 1.8+ | BSD | ✅ Approved |
| Hotkeys | pynput | 1.7+ | LGPL | ✅ Approved |
| File Watch | watchdog | 3.0+ | Apache 2.0 | ✅ Approved |
| Windows API | pywin32 | 300+ | PSF | ✅ Approved |

**Note**: UI Framework choice pending user decision (Phase 6 Compliance Review).

---

## Testing Standards

- **Minimum Coverage**: 85% per component, 90% overall
- **TDD Required**: Write tests BEFORE implementation (red-green-refactor)
- **Test Categories**: Unit, integration, edge cases, error handling
- **Test Naming**: Descriptive names (test_feature_does_what_when_condition)

---

## Documentation Standards

- **Module Docstrings**: Required for all modules
- **Class Docstrings**: Required for all classes
- **Method Docstrings**: Required for all public methods
- **Inline Comments**: For non-obvious logic
- **Type Hints**: Encouraged but not required

---

## Git Commit Standards

- **When to Commit**: After each phase completes (all tests passing)
- **Commit Message Format**:
  ```
  Phase {N}: {Component Name} - {Brief Description}

  - Feature 1
  - Feature 2
  - Test count: X/X passing
  - Coverage: Y%

  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>
  ```

---

## File Organization

```
quick-snippet-overlay/
├── .claude/
│   ├── CLAUDE.md                          # This file
│   ├── PHASE-COMPLIANCE-CHECKLIST.md      # Reusable template
│   ├── PHASE-COMPLETION-WORKFLOW.md       # Standard workflow
│   └── COMPLIANCE-ENFORCEMENT.md          # Enforcement strategy
├── src/
│   ├── __init__.py
│   ├── main.py                            # Entry point
│   ├── overlay_window.py                  # UI
│   ├── system_tray.py                     # Tray integration
│   ├── hotkey_manager.py                  # Global hotkeys
│   ├── snippet_manager.py                 # Snippet CRUD
│   ├── search_engine.py                   # Fuzzy search
│   ├── variable_handler.py                # Variable substitution
│   ├── variable_prompt_dialog.py          # Variable input
│   └── config_manager.py                  # Configuration
├── tests/
│   ├── test_*.py                          # Test files (mirror src/)
│   ├── conftest.py                        # Pytest fixtures
│   └── fixtures/                          # Test data
├── PHASE-{N}-COMPLETION-REPORT.md         # Phase completion docs
├── PHASE-{N}-COMPLIANCE-REVIEW.md         # Compliance verification docs
├── requirements.txt                        # Python dependencies
├── config.yaml                            # App configuration
└── snippets.yaml                          # Snippet data

```

---

## Key Lessons Learned (Phase 6)

### What Went Wrong
- Phase 5 used PySide6 instead of PyQt6 (PRD specified PyQt6)
- Phase 6 followed Phase 5 for "consistency" without checking PRD
- No compliance verification step existed
- Completion reports claimed "PyQt6-based" but code used PySide6

### Root Causes
1. No specification verification before coding
2. "Consistency with existing code" prioritized over "conformance to specs"
3. No document hierarchy (PRD should be authoritative)
4. Completion reports not audited against actual code

### How We Fixed It
1. ✅ Created compliance verification template
2. ✅ Made Step 13 mandatory in all phases
3. ✅ Established PRD as source of truth
4. ✅ Added self-enforcement protocol for Claude
5. ✅ Documented process for future phases

### Never Again
- ❌ Never assume existing code is correct
- ❌ Never skip PRD verification
- ❌ Never write completion report without compliance review
- ❌ Never prioritize "working code" over "correct specification"

---

## Quick Reference

**Starting New Phase?**
1. Read PRD section for phase
2. Read Implementation Plan section
3. Note ALL technology/library choices
4. Verify existing code matches (if continuing)

**Completing Phase?**
1. All tests passing? ✅
2. Coverage targets met? ✅
3. **Compliance verification done?** ← MANDATORY
4. User approved compliance? ✅
5. Only then: Write completion report

**Found Discrepancy?**
1. Document it (P0/P1/P2)
2. Present options to user
3. Get explicit decision
4. Fix OR document accepted deviation
5. Update PRD if deviation accepted

---

## Contact

- **Project Owner**: mikeh
- **Project Location**: C:\Users\mikeh\software_projects\quick-snippet-overlay
- **PRD Location**: C:\Users\mikeh\software_projects\brainstorming\PRD-quick-snippet-overlay-v2.md
- **Implementation Plan**: C:\Users\mikeh\software_projects\brainstorming\PHASED-IMPLEMENTATION-PLAN-v2.md

---

**Remember**: Compliance verification is not optional. It's the difference between "it works" and "it's correct."
