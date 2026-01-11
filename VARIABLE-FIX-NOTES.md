# Variable Substitution Fix Notes

## Problem
Variable names with spaces or hyphens (like `{{user name}}` or `{{short-description}}`) were silently ignored because the validation regex only allowed `[a-zA-Z0-9_]+`.

## Solution
Update `src/variable_handler.py` to accept any characters except `{` and `}` in variable names.

### Changes Required

**File: `src/variable_handler.py`**

1. **Line 38** - Update regex pattern:
```python
# FROM:
pattern = r"(?=\{\{(.+?)\}\})"

# TO:
pattern = r"(?=\{\{([^{}]+)\}\})"
```

2. **Lines 52-56** - Remove character validation (delete these lines):
```python
# DELETE THESE LINES:
# Validate variable name: alphanumeric + underscore only
if not re.match(r"^[a-zA-Z0-9_]+$", var_name):
    # Invalid variable name - skip it
    continue
```

3. **Update docstrings** to reflect that any characters are allowed except braces.

### Test Changes Required

**File: `tests/test_variable_handler.py`**

1. Update `test_invalid_variable_names()` to `test_variable_names_with_special_chars()` - hyphens and special chars should now be valid
2. Add tests for variables like `{{short-description}}` and `{{Describe the bug}}`
3. Add substitution tests for hyphenated variable names

## Branch Reference
The changes were implemented on branch `feature/add-variable` (PR #1).
Can be referenced with: `git show feature/add-variable:src/variable_handler.py`

## To Re-implement
Once the app is confirmed working:
1. Create new branch from master
2. Apply the changes above
3. Run tests: `python -m pytest tests/test_variable_handler.py -v`
4. Test manually with a snippet containing `{{user name}}` or `{{short-description}}`
