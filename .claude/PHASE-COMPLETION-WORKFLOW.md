# Phase Completion Workflow (With Compliance Verification)

**Purpose**: Standardized workflow for completing any phase with built-in compliance verification.

**Critical Change**: Added **Step 13** - Compliance Verification BEFORE writing completion report.

---

## Standard Phase Workflow (All Phases)

### Steps 1-12: Implementation & Testing
[Follow phase-specific handoff document]
- Install dependencies
- Write tests (TDD - RED phase)
- Implement code (TDD - GREEN phase)
- Verify coverage
- Run full test suite

### ✅ Step 13: COMPLIANCE VERIFICATION (NEW - REQUIRED)

**Status**: Required before Step 14 (Completion Report)

**Duration**: 30-45 minutes

**Objective**: Verify implementation conforms to PRD and Implementation Plan specifications

#### 13.1 Create Compliance Review Document
```bash
cd C:\Users\mikeh\software_projects\quick-snippet-overlay
cp .claude/PHASE-COMPLIANCE-CHECKLIST.md PHASE-{N}-COMPLIANCE-REVIEW.md
```

#### 13.2 Fill Out Compliance Checklist

Work through each section systematically:

**Section 1: Technology/Library Compliance** (5 min)
- Open PRD: `C:\Users\mikeh\software_projects\brainstorming\PRD-quick-snippet-overlay-v2.md`
- Find technology stack section
- Verify EVERY library specified matches implementation
- Command: `grep -r "^from\|^import" src/*.py | sort | uniq`

**Section 2: Functional Requirements** (10 min)
- Open PRD Core Features section
- Open Implementation Plan phase section
- List EVERY functional requirement
- Verify each is implemented (check tests + code)

**Section 3: Architecture/Design** (5 min)
- Verify file structure matches plan
- Check class/function signatures match specifications

**Section 4: Integration Points** (5 min)
- Verify dependencies on previous phases work as specified
- Verify interfaces provided to future phases are correct

**Section 5: Configuration** (3 min)
- Check config.yaml schema matches PRD
- Verify default values match

**Section 6: Testing** (5 min)
- Verify coverage meets targets
- Verify test categories cover all requirements

**Section 7-11: Documentation, Code Quality, Dependencies, Performance, Platform** (7 min)
- Quick verification of each area

#### 13.3 Flag ALL Discrepancies

For EACH discrepancy found:
1. Document in "Discrepancies Found" section
2. Classify severity:
   - **P0 Critical**: Blocks phase completion (e.g., wrong library used)
   - **P1 High**: Should fix but can document (e.g., 82% vs 85% coverage)
   - **P2 Low**: Document only (e.g., extra helper function)

#### 13.4 Present Findings to User

**Template Message**:
```
## Phase {N} Compliance Review Complete

I've completed the compliance verification. Here are the findings:

### ✅ COMPLIANT AREAS
- Technology stack: [list what matches]
- Functional requirements: [list what matches]
- Test coverage: [stats]

### ❌ DISCREPANCIES FOUND

**P0 Critical Issues** (Must fix):
1. [Issue 1: Description, Impact, Recommendation]
2. [Issue 2: ...]

**P1 High Issues** (Should fix or document):
1. [Issue 1: ...]

**P2 Low Issues** (Document only):
1. [Issue 1: ...]

### 🤔 DECISION REQUIRED

For each P0/P1 issue, I need your decision:
- Option A: Fix to match PRD (rework code)
- Option B: Accept deviation (update PRD to reflect implementation)
- Option C: Other approach

What should we do?

See full details in: PHASE-{N}-COMPLIANCE-REVIEW.md
```

#### 13.5 Get User Approval

**Do NOT proceed to Step 14** until user approves one of:
- ✅ "All compliant, proceed to completion report"
- ⚠️ "Accepted deviations documented, proceed"
- ❌ "Critical issues found, must fix before completing"

#### 13.6 Fix or Document Deviations

**If fixing code**:
- Make corrections
- Re-run tests
- Update compliance review document
- Get user re-approval

**If accepting deviations**:
- Update PRD/Implementation Plan to reflect reality
- Document justification in compliance review
- Get user approval on updated specs

---

### Step 14: Completion Report (AFTER Compliance Verification)

**Only proceed after Step 13 approved**

Write `PHASE-{N}-COMPLETION-REPORT.md` with:
- Implementation summary
- Test results
- **COMPLIANCE SECTION** (NEW):
  ```markdown
  ## Compliance Verification

  ✅ Compliance review completed: [Date]
  ✅ Review document: PHASE-{N}-COMPLIANCE-REVIEW.md

  **PRD Compliance**: [COMPLIANT / DEVIATIONS DOCUMENTED]
  **Implementation Plan Compliance**: [COMPLIANT / DEVIATIONS DOCUMENTED]

  **Approved Deviations**:
  1. [Deviation 1: Description and justification]
  2. [Deviation 2: ...]

  **Compliance Approval**: [User name, Date]
  ```

---

### Step 15: Manual Integration Testing

[Continue as before]

---

## Enforcement Mechanism

### How to Ensure Compliance Verification Happens

**For Users:**
1. Add to handoff documents: "Step 13: Compliance Verification (REQUIRED)"
2. Explicitly tell Claude: "Do not write completion report until compliance verification is complete and approved"

**For Claude:**
1. **Self-check before completion report**:
   - "Have I run compliance verification?"
   - "Did user approve the compliance review?"
   - If NO to either: Stop and do compliance verification

2. **Completion report must include compliance section**
   - If writing completion report without compliance section = process violation
   - Automatically triggers self-reminder to go back and do compliance check

---

## Template for Future Phase Handoffs

Add this to every phase handoff document:

```markdown
### Step {N-1}: Compliance Verification (REQUIRED - 30-45 min)

**DO NOT PROCEED TO COMPLETION REPORT WITHOUT THIS STEP**

1. Copy `.claude/PHASE-COMPLIANCE-CHECKLIST.md` to `PHASE-{N}-COMPLIANCE-REVIEW.md`
2. Fill out ALL sections of the checklist
3. Run verification commands to check:
   - Technology/library choices match PRD
   - Functional requirements all implemented
   - File structure matches plan
   - Test coverage meets targets
4. Flag ALL discrepancies (P0/P1/P2)
5. Present findings to user
6. Get user approval before proceeding
7. Fix critical issues OR document accepted deviations

**Compliance verification is MANDATORY. Phase is not complete until user approves compliance review.**

See: `.claude/PHASE-COMPLETION-WORKFLOW.md` for detailed instructions.
```

---

## Example: How This Would Have Caught PyQt6/PySide6 Issue

### Phase 5 Compliance Verification (Would Have Caught It)

**Step 13.2 - Section 1: Technology Compliance**

```bash
# Check PRD
grep -i "pyqt\|pyside" PRD-quick-snippet-overlay-v2.md
# Output: | **UI Framework** | PyQt6 | Native Windows look... |

# Check implementation
grep -r "^from.*Qt" src/*.py
# Output: from PySide6.QtWidgets import...
```

**Result**: ❌ MISMATCH DETECTED

**Compliance Review Finding**:
```
P0 CRITICAL ISSUE:
- PRD Specifies: PyQt6
- Implementation Uses: PySide6
- Impact: Does not conform to approved specifications
- Recommendation: Fix to use PyQt6 OR get PRD amended
```

**User Decision Required**: Cannot proceed to completion without resolution.

### Phase 6 Would Have Been Blocked

Phase 6 compliance verification would have found:
- Phase 5 used PySide6 (wrong)
- Phase 6 continued with PySide6 (wrong)
- Cascade of non-compliance

**Outcome**: Both phases fixed before marking complete.

---

## Benefits of This Process

1. ✅ **Catches specification deviations early** (before phase marked complete)
2. ✅ **Forces explicit user decision** on any deviations
3. ✅ **Creates audit trail** (compliance review documents)
4. ✅ **Prevents cascade issues** (bad phase doesn't contaminate next phase)
5. ✅ **Improves documentation** (PRD stays accurate OR deviations are documented)

---

## Integration with Existing Process

### Before (Old Process)
```
Step 1-12: Implementation & Testing
Step 13: Write Completion Report ← Could have deviations
Step 14: Manual Testing
```

### After (New Process)
```
Step 1-12: Implementation & Testing
Step 13: Compliance Verification (NEW) ← Catches deviations
  → If issues: Fix or get approval
  → Only proceed when user approves
Step 14: Write Completion Report (includes compliance section)
Step 15: Manual Testing
```

---

## Next Steps

1. ✅ Template created: `.claude/PHASE-COMPLIANCE-CHECKLIST.md`
2. ✅ Workflow documented: `.claude/PHASE-COMPLETION-WORKFLOW.md`
3. ⏳ Run compliance verification for Phase 6 NOW (retroactive)
4. ⏳ Fix PyQt6/PySide6 issue based on user decision
5. ⏳ Update all future handoff documents to include Step 13

**For Current Situation:**
Let's run Phase 6 compliance verification NOW to catch any other issues beyond PyQt6/PySide6.
