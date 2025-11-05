# Phase Compliance Verification Checklist

**Purpose**: Verify that phase implementation conforms to PRD and Implementation Plan specifications BEFORE marking phase complete.

**When to Use**: After all tests pass, before writing completion report.

**How to Use**:
1. Copy this checklist to `PHASE-{N}-COMPLIANCE-REVIEW.md`
2. Fill out each section systematically
3. Flag ALL discrepancies
4. Get user approval for any deviations
5. Only mark phase complete after compliance verified

---

## Phase Information

- **Phase Number**: [e.g., 6]
- **Phase Name**: [e.g., System Tray & Hotkey Integration]
- **Reviewer**: [e.g., Claude Code]
- **Review Date**: [YYYY-MM-DD]
- **Status**: [ ] COMPLIANT / [ ] DEVIATIONS FOUND / [ ] NON-COMPLIANT

---

## Section 1: Technology/Library Compliance

### 1.1 Review PRD Technology Stack

**PRD Section**: [e.g., Section 3.2 - Technology Stack]

**Specified Technologies**:
| Component | PRD Specifies | Implementation Uses | Status |
|-----------|---------------|---------------------|--------|
| Example: UI Framework | PyQt6 | PySide6 | ❌ MISMATCH |
| Example: Hotkey Library | pynput | pynput | ✅ MATCH |

**Instructions**:
1. Open PRD: `PRD-quick-snippet-overlay-v2.md`
2. Find technology stack section (usually Section 3.x or table)
3. List EVERY technology specified for this phase
4. Grep actual code to verify what's used:
   ```bash
   cd src/
   grep -r "^from\|^import" *.py | grep -i "qt\|hotkey\|yaml\|etc"
   ```
5. Mark each as MATCH ✅ or MISMATCH ❌

**Discrepancies Found**: [List any mismatches]

**Resolution Required**: [Y/N] - If Y, describe what needs to change

---

### 1.2 Review Implementation Plan Technology Choices

**Implementation Plan Section**: [e.g., Phase 6, Lines 1045-1350]

**Specified Technologies**:
| Component | Plan Specifies | Implementation Uses | Status |
|-----------|----------------|---------------------|--------|
| | | | |

**Discrepancies Found**: [List any mismatches]

---

## Section 2: Functional Requirements Compliance

### 2.1 PRD Functional Requirements

**PRD Section**: [e.g., Section 4.x - Core Features, Section 5.x - Feature Details]

**Requirements Checklist**:
| Req ID | Requirement Description | Implemented? | Evidence |
|--------|------------------------|--------------|----------|
| F1 | Example: Ctrl+Shift+Space hotkey | ✅ YES | test_hotkey_manager.py:78 |
| F2 | Example: System tray icon | ✅ YES | test_system_tray.py:52 |
| F3 | Example: Single instance enforcement | ✅ YES | test_main.py:56 |

**Instructions**:
1. Open PRD Section for Core Features
2. Extract EVERY functional requirement for this phase
3. Verify each is implemented (check code + tests)
4. Provide evidence (test name, code line, or explanation)

**Missing Requirements**: [List any unimplemented features]

**Extra Features**: [List any features NOT in PRD - may be scope creep]

---

### 2.2 Implementation Plan Requirements

**Implementation Plan Section**: [e.g., Phase 6 Objectives]

**Requirements Checklist**:
| Requirement | Implemented? | Evidence |
|-------------|--------------|----------|
| | | |

**Missing Requirements**: [List any gaps]

---

## Section 3: Architecture/Design Compliance

### 3.1 Component Structure

**PRD Specifies**: [e.g., "main.py, system_tray.py, hotkey_manager.py"]

**Implementation Has**:
```bash
ls -la src/*.py
```

**File Structure Comparison**:
| PRD/Plan Specifies | Actual Files | Status |
|--------------------|--------------|--------|
| main.py | src/main.py | ✅ MATCH |
| system_tray.py | src/system_tray.py | ✅ MATCH |

**Discrepancies**: [List any missing/extra files]

---

### 3.2 API/Interface Compliance

**PRD/Plan Specifies**: [e.g., "HotkeyManager should emit hotkey_pressed signal"]

**Implementation Verification**:
```bash
grep -n "class HotkeyManager\|def.*signal\|Signal()" src/hotkey_manager.py
```

**Interface Checklist**:
| Specified Interface | Implemented? | Evidence |
|---------------------|--------------|----------|
| | | |

**Discrepancies**: [List any API differences]

---

## Section 4: Integration Point Compliance

### 4.1 Dependencies on Previous Phases

**PRD/Plan Specifies**: [e.g., "Phase 6 depends on ConfigManager.get('hotkey')"]

**Integration Verification**:
| Integration Point | Specified | Implemented | Status |
|-------------------|-----------|-------------|--------|
| Example: Get hotkey from config | ConfigManager.get('hotkey') | config_manager.get('hotkey') | ✅ MATCH |

**Integration Issues**: [List any mismatches]

---

### 4.2 Interfaces Provided to Future Phases

**PRD/Plan Specifies**: [e.g., "Phase 7 will use main.py as entry point"]

**Verification**:
| Interface Provided | Specified | Implemented | Status |
|--------------------|-----------|-------------|--------|
| | | | |

**Issues**: [List any problems for downstream phases]

---

## Section 5: Configuration Compliance

### 5.1 Configuration Schema

**PRD/Plan Specifies**: [e.g., "config.yaml should have 'hotkey' field"]

**Actual Configuration**:
```bash
cat config.yaml
grep -n "DEFAULT_CONFIG\|schema" src/config_manager.py
```

**Schema Verification**:
| Config Field | Specified | Implemented | Status |
|--------------|-----------|-------------|--------|
| | | | |

**Discrepancies**: [List any missing/extra config fields]

---

## Section 6: Testing Compliance

### 6.1 Test Coverage Requirements

**PRD/Plan Specifies**: [e.g., "≥85% coverage for Phase 6 components"]

**Actual Coverage**:
```bash
pytest --cov=src --cov-report=term
```

| Component | Required Coverage | Actual Coverage | Status |
|-----------|-------------------|-----------------|--------|
| main.py | ≥85% | 82% | ⚠️ CLOSE |
| system_tray.py | ≥85% | 97% | ✅ PASS |

**Coverage Issues**: [List components below threshold]

---

### 6.2 Test Categories

**PRD/Plan Specifies**: [e.g., "Test single instance enforcement, hotkey registration, tray menu actions"]

**Test Categories Verification**:
| Test Category | Required? | Tests Present | Status |
|---------------|-----------|---------------|--------|
| | | | |

**Missing Test Categories**: [List any gaps]

---

## Section 7: Documentation Compliance

### 7.1 Required Documentation

**PRD/Plan Specifies**: [e.g., "Docstrings for all public methods"]

**Documentation Verification**:
```bash
grep -c "def " src/main.py
grep -c '"""' src/main.py
```

| Requirement | Status |
|-------------|--------|
| Docstrings for classes | ✅ / ❌ |
| Docstrings for public methods | ✅ / ❌ |
| Module-level docstrings | ✅ / ❌ |
| Inline comments for complex logic | ✅ / ❌ |

**Documentation Issues**: [List any gaps]

---

## Section 8: Code Quality Compliance

### 8.1 Code Standards

**PRD/Plan Specifies**: [e.g., "Type hints, PEP 8 compliance"]

**Verification**:
```bash
# Check for type hints
grep -c "def.*->" src/main.py
# Check imports structure
grep "^from\|^import" src/main.py
```

**Standards Checklist**:
| Standard | Required | Status |
|----------|----------|--------|
| Type hints | Yes/No | ✅ / ❌ |
| PEP 8 compliance | Yes/No | ✅ / ❌ |
| Import organization | Yes/No | ✅ / ❌ |

**Code Quality Issues**: [List any violations]

---

## Section 9: Dependency/Requirements Compliance

### 9.1 Dependency Verification

**PRD/Plan Specifies**: [e.g., "pynput, keyboard, pywin32"]

**Actual requirements.txt**:
```bash
cat requirements.txt | grep -E "pynput|keyboard|pywin32|PyQt|PySide"
```

**Dependency Verification**:
| Dependency | PRD Specifies | requirements.txt Has | Status |
|------------|---------------|----------------------|--------|
| | | | |

**Issues**:
- [ ] Extra dependencies not in PRD
- [ ] Missing dependencies from PRD
- [ ] Version mismatches

---

## Section 10: Performance Requirements Compliance

### 10.1 Performance Targets

**PRD Specifies**: [e.g., "Hotkey response <100ms"]

**Measured Performance**:
```bash
# Run performance tests
pytest -k "performance" -v
```

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| | | | |

**Performance Issues**: [List any failures to meet targets]

---

## Section 11: Platform/Environment Compliance

### 11.1 Platform Requirements

**PRD Specifies**: [e.g., "Windows 11, Python 3.10+"]

**Implementation Verification**:
```bash
grep -n "sys.platform\|platform.system" src/*.py
python --version
```

**Platform Checklist**:
| Requirement | Specified | Verified | Status |
|-------------|-----------|----------|--------|
| OS | Windows 11 | [Check] | ✅ / ❌ |
| Python Version | 3.10+ | [Check] | ✅ / ❌ |

**Platform Issues**: [List any problems]

---

## COMPLIANCE SUMMARY

### Critical Discrepancies (Must Fix)
1. [List P0 issues that block phase completion]
2.

### Non-Critical Discrepancies (Document & Accept)
1. [List acceptable deviations with justification]
2.

### Extra Features (Not in PRD)
1. [List scope additions]
2.

### Recommendations
1. [Suggestions for fixes or next steps]
2.

---

## FINAL VERDICT

**Overall Compliance Status**:
- [ ] ✅ FULLY COMPLIANT - All requirements met, proceed to completion
- [ ] ⚠️ SUBSTANTIALLY COMPLIANT - Minor issues documented, acceptable to proceed
- [ ] ❌ NON-COMPLIANT - Critical issues found, must fix before phase completion

**Required Actions Before Phase Completion**:
1. [Action item 1]
2. [Action item 2]

**Approved By**: [User approval required]

**Date Approved**: [YYYY-MM-DD]

---

## APPENDIX: Commands Used for Verification

```bash
# Technology verification
grep -r "^from\|^import" src/*.py | grep -i "qt"

# File structure
ls -la src/ tests/

# Coverage
pytest --cov=src --cov-report=term

# Dependencies
cat requirements.txt

# Documentation check
grep -c '"""' src/*.py

# Performance tests
pytest -k "performance" -v
```
