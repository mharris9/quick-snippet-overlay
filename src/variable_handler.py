"""
Variable Handler Module

Provides functions to detect and substitute variables in snippet content.

Variable Syntax:
- Simple variable: {{variable_name}}
- Variable with default: {{variable_name:default_value}}

Variable names must contain only alphanumeric characters and underscores.
"""

import re
from typing import Optional


def detect_variables(content: str) -> list[dict[str, Optional[str]]]:
    """
    Detect all variables in content and return their metadata.

    Args:
        content: String content potentially containing variables

    Returns:
        List of dictionaries with 'name' and 'default' keys.
        Example: [{'name': 'app_name', 'default': 'app'}, {'name': 'port', 'default': None}]

    Edge Cases:
        - Invalid variable names (with hyphens, spaces) are ignored
        - Empty variable names {{}} are ignored
        - Duplicate variables are deduplicated (returns each unique variable once)
        - Nested braces: {{{var}}} will detect {{var}} as valid variable
    """
    # Regex pattern to match {{...}}
    # Use lookahead (?=...) to find ALL possible {{...}} patterns including overlapping ones
    # This handles cases like {{{var}}} which contains both {{{var}} and {{var}}
    # We use non-greedy .+? to stop at the first }}
    pattern = r'(?=\{\{(.+?)\}\})'

    # findall with lookahead returns only the captured groups
    matches = re.findall(pattern, content)

    variables = []
    seen_names = set()

    for match in matches:
        # Parse variable name and optional default value
        # Split on first colon only (to handle defaults like "https://example.com")
        parts = match.split(':', 1)
        var_name = parts[0].strip()

        # Validate variable name: alphanumeric + underscore only
        if not re.match(r'^[a-zA-Z0-9_]+$', var_name):
            # Invalid variable name - skip it
            continue

        # Skip empty variable names
        if not var_name:
            continue

        # Check if we've already seen this variable (deduplication)
        if var_name in seen_names:
            continue

        seen_names.add(var_name)

        # Extract default value if present
        default_value = parts[1] if len(parts) > 1 else None

        variables.append({
            'name': var_name,
            'default': default_value
        })

    return variables


def substitute_variables(content: str, values: dict[str, str]) -> str:
    """
    Replace all variable occurrences with provided or default values.

    Args:
        content: String content containing variables
        values: Dictionary mapping variable names to replacement values

    Returns:
        Content with all variables replaced

    Behavior:
        - Replaces all occurrences of {{var}} or {{var:default}}
        - If variable value is provided in `values`, uses that
        - If not provided but default exists, uses default
        - If neither provided nor default exists, raises ValueError

    Edge Cases:
        - Multiple occurrences of same variable are all replaced
        - Invalid variable names are left as-is (not substituted)
    """
    # First, detect all variables to understand what we're working with
    variables = detect_variables(content)

    # Build complete substitution map (provided values + defaults)
    substitutions = {}

    for var in variables:
        var_name = var['name']

        if var_name in values:
            # Use provided value
            substitutions[var_name] = values[var_name]
        elif var['default'] is not None:
            # Use default value
            substitutions[var_name] = var['default']
        else:
            # No value provided and no default - error
            raise ValueError(
                f"No value provided for variable '{var_name}' and no default specified"
            )

    # Perform substitution
    # We need to handle both {{var}} and {{var:default}} forms
    result = content

    for var_name, replacement_value in substitutions.items():
        # Pattern to match {{var_name}} or {{var_name:anything}}
        # Use word boundaries and escape the variable name for regex safety
        pattern = r'\{\{' + re.escape(var_name) + r'(?::[^}]*)?\}\}'
        # Use lambda to avoid backslash interpretation in replacement string
        result = re.sub(pattern, lambda m: replacement_value, result)

    return result


class VariableHandler:
    """
    Wrapper class for variable handling functions.

    Provides object-oriented interface to detect_variables and substitute_variables.
    """

    def detect_variables(self, content: str) -> list[dict[str, Optional[str]]]:
        """Detect variables in content."""
        return detect_variables(content)

    def substitute_variables(self, content: str, values: dict[str, str]) -> str:
        """Substitute variables in content with provided values."""
        return substitute_variables(content, values)
