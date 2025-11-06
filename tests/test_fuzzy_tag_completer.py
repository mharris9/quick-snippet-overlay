"""
Tests for FuzzyTagCompleter class.

This module tests fuzzy matching functionality for tag autocomplete.
"""

import pytest
from src.fuzzy_tag_completer import FuzzyTagCompleter


@pytest.fixture
def basic_tags():
    """Common tag list for testing."""
    return ["python", "javascript", "testing", "pyside", "pyqt"]


@pytest.fixture
def completer(basic_tags):
    """FuzzyTagCompleter instance with basic tags."""
    return FuzzyTagCompleter(basic_tags)


def test_exact_match(completer):
    """Test exact match returns the matching tag."""
    # Setup: FuzzyTagCompleter with tags ["python", "javascript", "testing", "pyside", "pyqt"]
    # Action: splitPath("python")
    # Expected: ["python"] (exact match, score=100)
    result = completer.splitPath("python")
    assert "python" in result
    # Exact match should be prioritized (first in list)
    assert result[0] == "python"


def test_typo_tolerance(basic_tags):
    """Test typo tolerance - missing character still matches."""
    # Setup: FuzzyTagCompleter with ["python", "javascript"]
    completer = FuzzyTagCompleter(["python", "javascript"])
    # Action: splitPath("pyton")
    # Expected: ["python"] (fuzzy match despite missing 'h')
    result = completer.splitPath("pyton")
    assert "python" in result


def test_prefix_match(basic_tags):
    """Test prefix matching returns all tags starting with prefix."""
    # Setup: FuzzyTagCompleter with ["python", "pyside", "pyqt", "javascript"]
    completer = FuzzyTagCompleter(["python", "pyside", "pyqt", "javascript"])
    # Action: splitPath("py")
    # Expected: Contains "python", "pyside", "pyqt" (all match prefix)
    result = completer.splitPath("py")
    assert "python" in result
    assert "pyside" in result
    assert "pyqt" in result
    # javascript should not be in results (doesn't match well)
    assert "javascript" not in result


def test_no_match_below_threshold(basic_tags):
    """Test that tags scoring below threshold are not returned."""
    # Setup: FuzzyTagCompleter with ["python", "javascript"]
    completer = FuzzyTagCompleter(["python", "javascript"])
    # Action: splitPath("xyz")
    # Expected: [] (no tags score above 60)
    result = completer.splitPath("xyz")
    assert result == []


def test_case_insensitive_matching(basic_tags):
    """Test case-insensitive fuzzy matching."""
    # Setup: FuzzyTagCompleter with ["Python", "JavaScript"]
    completer = FuzzyTagCompleter(["Python", "JavaScript"])
    # Action: splitPath("PYTHON")
    # Expected: ["Python"] (case-insensitive)
    result = completer.splitPath("PYTHON")
    assert "Python" in result


def test_score_sorting(basic_tags):
    """Test that results are sorted by score (best match first)."""
    # Setup: FuzzyTagCompleter with ["python", "pyside", "testing"]
    completer = FuzzyTagCompleter(["python", "pyside", "testing"])
    # Action: splitPath("pyt")
    # Expected: "python" comes before "pyside" (better score)
    result = completer.splitPath("pyt")

    # Both should be in results
    assert "python" in result

    # python should come before pyside (better match for "pyt")
    if len(result) >= 2:
        python_idx = result.index("python")
        if "pyside" in result:
            pyside_idx = result.index("pyside")
            assert python_idx < pyside_idx


def test_empty_input(completer):
    """Test that empty input returns no suggestions."""
    # Setup: FuzzyTagCompleter with ["python"]
    # Action: splitPath("")
    # Expected: [] (no suggestions for empty input)
    result = completer.splitPath("")
    assert result == []


def test_limit_suggestions():
    """Test that suggestions are limited to 10 max."""
    # Setup: FuzzyTagCompleter with 20 tags starting with "test-"
    tags = [f"test-{i:02d}" for i in range(20)]
    completer = FuzzyTagCompleter(tags)

    # Action: splitPath("test")
    # Expected: Returns max 10 suggestions (not all 20)
    result = completer.splitPath("test")
    assert len(result) <= 10


def test_update_tags_method(basic_tags):
    """Test that update_tags() method updates the tag list."""
    # Setup: FuzzyTagCompleter with ["old-tag"]
    completer = FuzzyTagCompleter(["old-tag"])

    # Verify initial state
    result = completer.splitPath("old")
    assert "old-tag" in result

    # Action: update_tags(["new-tag"]), then splitPath("new")
    completer.update_tags(["new-tag"])

    # Expected: ["new-tag"] (model updated)
    result = completer.splitPath("new")
    assert "new-tag" in result

    # Old tag should no longer match
    result_old = completer.splitPath("old")
    assert "old-tag" not in result_old
