"""
Test suite for variable_handler.py

Tests variable detection, parsing, validation, and substitution logic.
Following TDD approach: tests written FIRST, implementation SECOND.
"""

import pytest
from src.variable_handler import detect_variables, substitute_variables


# ===========================
# Detection Tests (Tests 1-8)
# ===========================

def test_no_variables():
    """Test content with no variables returns empty list."""
    content = "This is plain text with no variables."
    result = detect_variables(content)
    assert result == []

    content2 = "Some text with single braces { but not variables }."
    result2 = detect_variables(content2)
    assert result2 == []


def test_simple_variable():
    """Test detection of simple variable without default value."""
    content = "Get-Item {{filepath}}"
    result = detect_variables(content)

    assert len(result) == 1
    assert result[0]['name'] == 'filepath'
    assert result[0]['default'] is None


def test_variable_with_default():
    """Test detection of variable with default value."""
    content = "flask --app {{app_name:app}} run"
    result = detect_variables(content)

    assert len(result) == 1
    assert result[0]['name'] == 'app_name'
    assert result[0]['default'] == 'app'


def test_multiple_variables():
    """Test detection of multiple distinct variables."""
    content = "flask --app {{app_name:app}} run --port {{port:5000}}"
    result = detect_variables(content)

    assert len(result) == 2

    # Variables should be in order of first appearance
    assert result[0]['name'] == 'app_name'
    assert result[0]['default'] == 'app'

    assert result[1]['name'] == 'port'
    assert result[1]['default'] == '5000'


def test_duplicate_variable():
    """Test that duplicate variables are deduplicated."""
    content = "Clone {{repo}} to {{clone_dir}}/{{repo}}"
    result = detect_variables(content)

    # Should return only unique variables
    assert len(result) == 2

    var_names = [v['name'] for v in result]
    assert 'repo' in var_names
    assert 'clone_dir' in var_names

    # Each variable should appear only once
    assert var_names.count('repo') == 1


def test_invalid_variable_names():
    """Test that variables with invalid names (hyphens, spaces) are ignored."""
    # Variables with hyphens should be ignored
    content1 = "Test {{app-name}} invalid"
    result1 = detect_variables(content1)
    assert result1 == []

    # Variables with spaces should be ignored
    content2 = "Test {{app name}} invalid"
    result2 = detect_variables(content2)
    assert result2 == []

    # Valid variable with underscore should work
    content3 = "Test {{app_name}} valid"
    result3 = detect_variables(content3)
    assert len(result3) == 1
    assert result3[0]['name'] == 'app_name'

    # Mix of valid and invalid
    content4 = "{{valid_var}} and {{invalid-var}} and {{another_valid}}"
    result4 = detect_variables(content4)
    assert len(result4) == 2
    assert result4[0]['name'] == 'valid_var'
    assert result4[1]['name'] == 'another_valid'


def test_nested_braces_literal():
    """Test that nested braces are treated as literal text."""
    # Outer braces should not be interpreted as variable
    content = "This has {{{var}}} nested braces"
    result = detect_variables(content)

    # Should detect the inner {{var}} as a valid variable
    # The outer single braces are literal
    assert len(result) == 1
    assert result[0]['name'] == 'var'


def test_empty_variable_name():
    """Test that empty variable names {{}} are ignored."""
    content = "Empty {{}} variable should be ignored"
    result = detect_variables(content)
    assert result == []

    # Mix of empty and valid
    content2 = "{{valid}} and {{}} and {{another}}"
    result2 = detect_variables(content2)
    assert len(result2) == 2
    assert result2[0]['name'] == 'valid'
    assert result2[1]['name'] == 'another'


# ==============================
# Substitution Tests (Tests 9-10)
# ==============================

def test_substitute_variables():
    """Test basic variable substitution with provided values and defaults."""
    # Test with provided value
    content = "Get-Item {{filepath}}"
    values = {'filepath': r'C:\temp\file.txt'}
    result = substitute_variables(content, values)
    assert result == r"Get-Item C:\temp\file.txt"

    # Test with default value (no value provided)
    content2 = "flask --app {{app_name:app}} run --port {{port:5000}}"
    values2 = {}  # No values provided, should use defaults
    result2 = substitute_variables(content2, values2)
    assert result2 == "flask --app app run --port 5000"

    # Test mix of provided values and defaults
    content3 = "flask --app {{app_name:app}} run --port {{port:5000}}"
    values3 = {'app_name': 'myapp'}  # Provide app_name, use default for port
    result3 = substitute_variables(content3, values3)
    assert result3 == "flask --app myapp run --port 5000"

    # Test default value with colon (URL)
    content4 = "Visit {{url:https://example.com}}"
    values4 = {}
    result4 = substitute_variables(content4, values4)
    assert result4 == "Visit https://example.com"

    # Test error when no value provided and no default
    content5 = "Get-Item {{filepath}}"
    values5 = {}
    with pytest.raises(ValueError, match="No value provided for variable 'filepath'"):
        substitute_variables(content5, values5)


def test_substitute_multiple_occurrences():
    """Test that multiple occurrences of same variable are all replaced."""
    # Multiple occurrences of same variable
    content = "Clone {{repo}} to {{clone_dir}}/{{repo}}"
    values = {'repo': 'MyApp', 'clone_dir': r'C:\Projects'}
    result = substitute_variables(content, values)
    assert result == r"Clone MyApp to C:\Projects/MyApp"

    # Verify both occurrences of {{repo}} were replaced
    assert 'MyApp' in result
    assert result.count('MyApp') == 2
    assert '{{repo}}' not in result

    # Test with variables that have defaults
    content2 = "Server: {{host:localhost}}, Port: {{port:8080}}, Connect to {{host:localhost}}:{{port:8080}}"
    values2 = {'host': 'example.com'}  # Only provide host, use default for port
    result2 = substitute_variables(content2, values2)
    assert result2 == "Server: example.com, Port: 8080, Connect to example.com:8080"
    assert 'example.com' in result2
    assert result2.count('example.com') == 2
    assert result2.count('8080') == 2
