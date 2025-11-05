# Compliance Verification Enforcement Strategy

**Goal**: Guarantee compliance verification happens in EVERY phase, not optional.

---

## Strategy 1: Update ALL Future Handoff Documents

### Template for Phase Handoff Documents

**Add this as Step 13 in EVERY phase handoff**:

```markdown
### Step 13: COMPLIANCE VERIFICATION (MANDATORY - 30-45 min)

⚠️ **CRITICAL**: This step is REQUIRED before Step 14 (Completion Report)

**DO NOT WRITE COMPLETION REPORT WITHOUT COMPLIANCE VERIFICATION**

#### 13.1 Copy Compliance Template
```powershell
cd C:\Users\mikeh\software_projects\quick-snippet-overlay
Copy-Item .claude\PHASE-COMPLIANCE-CHECKLIST.md PHASE-{N}-COMPLIANCE-REVIEW.md
```

#### 13.2 Fill Out ALL Sections
Work through checklist systematically (see `.claude/PHASE-COMPLETION-WORKFLOW.md`)

#### 13.3 Verification Commands
```powershell
# Technology stack
grep -r "^from\|^import" src/*.py | grep -i "relevant_libs"

# Coverage
pytest --cov=src --cov-report=term

# File structure
ls -la src/ tests/

# Dependencies
cat requirements.txt | grep -E "library_names"
```

#### 13.4 Document ALL Discrepancies
Flag as P0/P1/P2, present to user

#### 13.5 Get User Approval
- ✅ "Compliant, proceed"
- ⚠️ "Accepted deviations, proceed"
- ❌ "Must fix critical issues"

**ENFORCEMENT**: Claude will refuse to write completion report if compliance verification not completed and approved.

See: `.claude/PHASE-COMPLIANCE-CHECKLIST.md` for full template
See: `.claude/PHASE-COMPLETION-WORKFLOW.md` for detailed instructions
```

---

## Strategy 2: Add to Claude Configuration (.claude/settings.local.json)

### Create Compliance Hook

```json
{
  "hooks": {
    "pre-completion-report": "compliance-verification-check"
  },
  "compliance": {
    "enabled": true,
    "required_before_completion": true,
    "checklist_path": ".claude/PHASE-COMPLIANCE-CHECKLIST.md"
  }
}
```

**Note**: This is aspirational - Claude doesn't currently support custom hooks, but documents the intent.

---

## Strategy 3: Claude Self-Enforcement Protocol

### Built-in Self-Check Before Completion Reports

When Claude is asked to write a completion report, Claude MUST:

**Step 1: Self-Check Questions**
```
BEFORE writing any completion report, ask myself:
1. Has compliance verification been completed for this phase?
2. Is there a PHASE-{N}-COMPLIANCE-REVIEW.md file?
3. Did the user approve the compliance review?
4. Are all P0 critical issues resolved or accepted?

IF answer to ANY question is NO:
  → STOP immediately
  → Message user: "Compliance verification required before completion report"
  → Guide user through compliance process
  → DO NOT write completion report
```

**Step 2: Refuse Non-Compliant Completion**
```
User: "Write the Phase X completion report"

Claude Self-Check:
- Compliance review file exists? [Check .claude/ or project root]
- User approved compliance? [Check for approval statement]

IF NOT:
  Response: "I cannot write the completion report yet. Phase completion
  workflow requires compliance verification first (Step 13). Let me guide
  you through it..."

  [Then launch compliance verification process]
```

**Step 3: Validate Completion Report Structure**
```
Every completion report MUST include:

## Compliance Verification Section

✅ Compliance review completed: [Date]
✅ Review document: PHASE-{N}-COMPLIANCE-REVIEW.md
✅ User approved: [Date, Name]

**PRD Compliance**: [COMPLIANT / DEVIATIONS DOCUMENTED]
**Implementation Plan Compliance**: [COMPLIANT / DEVIATIONS DOCUMENTED]

**Approved Deviations** (if any):
1. [Deviation description and justification]

IF section missing → Refuse to mark complete
```

---

## Strategy 4: Update .claude/CLAUDE.md Project Instructions

### Add Compliance Requirement to Project Instructions

<function_calls>
<invoke name="Read">
<parameter name="file_path">C:\Users\mikeh\software_projects\quick-snippet-overlay\.claude\CLAUDE.md