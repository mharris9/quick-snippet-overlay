"""
Test suite for search_engine.py - Fuzzy search with typo tolerance

This test suite follows the TDD approach:
1. Write tests first (RED phase)
2. Implement to pass tests (GREEN phase)
3. Refactor while keeping tests passing (REFACTOR phase)

Test Coverage:
- Basic fuzzy search across multiple fields
- Multi-field search with weighted scoring
- Typo tolerance (Levenshtein distance)
- Empty query handling
- No results scenarios
- Performance benchmarks (200 snippets <100ms)
- Special character handling
- Unicode support
- Result ranking by relevance
"""

import pytest
import time
from pathlib import Path
from src.snippet_manager import SnippetManager
from src.search_engine import SearchEngine


@pytest.fixture
def search_snippets_file():
    """Path to search test fixtures."""
    return Path(__file__).parent / "fixtures" / "search_snippets.yaml"


@pytest.fixture
def snippet_manager(search_snippets_file):
    """Initialize SnippetManager with search test fixtures."""
    manager = SnippetManager(str(search_snippets_file))
    snippets = manager.load()
    return manager


@pytest.fixture
def snippets(snippet_manager):
    """Load snippets for testing."""
    return snippet_manager.snippets


@pytest.fixture
def search_engine(snippets):
    """Initialize SearchEngine with test snippets."""
    return SearchEngine(snippets)


# ============================================================================
# Test 1: Basic Fuzzy Search
# ============================================================================


def test_basic_fuzzy_search(search_engine):
    """Test basic fuzzy search returns relevant results."""
    results = search_engine.search("flask")

    # Should return Flask-related snippets
    assert len(results) > 0, "Search should return results for 'flask'"

    # Results should contain snippet and score
    for result in results:
        assert "snippet" in result, "Result should contain 'snippet' key"
        assert "score" in result, "Result should contain 'score' key"
        assert isinstance(result["score"], (int, float)), "Score should be numeric"
        assert 0 <= result["score"] <= 100, "Score should be between 0 and 100"

    # First result should be Flask-related (name or tags contain 'flask')
    first_snippet = results[0]["snippet"]
    snippet_text = f"{first_snippet.name} {' '.join(first_snippet.tags)} {first_snippet.description}".lower()
    assert "flask" in snippet_text, "First result should be Flask-related"


# ============================================================================
# Test 2: Multi-Field Search
# ============================================================================


def test_multi_field_search(search_engine):
    """Test query matches across name, description, tags, and content."""
    # Search for "powershell" - should match in tags and content
    results = search_engine.search("powershell")

    assert len(results) > 0, "Should find PowerShell snippets"

    # Check that results contain PowerShell in at least one field
    for result in results[:3]:  # Check top 3 results
        snippet = result["snippet"]
        found_in_fields = (
            "powershell" in snippet.name.lower()
            or "powershell" in snippet.description.lower()
            or any("powershell" in tag.lower() for tag in snippet.tags)
            or "powershell" in snippet.content.lower()
        )
        assert (
            found_in_fields
        ), f"Snippet '{snippet.name}' should contain 'powershell' in at least one field"


# ============================================================================
# Test 3: Scoring Weights
# ============================================================================


def test_scoring_weights(search_engine):
    """Test that name matches are ranked higher than content matches."""
    # Search for "flask" - should prioritize name matches over content
    results = search_engine.search("flask")

    assert len(results) >= 2, "Should find multiple Flask snippets"

    # Snippets with "flask" in name should rank higher than those with "flask" only in content
    name_match_scores = []
    content_only_scores = []

    for result in results:
        snippet = result["snippet"]
        if "flask" in snippet.name.lower():
            name_match_scores.append(result["score"])
        elif "flask" in snippet.content.lower() and "flask" not in snippet.name.lower():
            content_only_scores.append(result["score"])

    # Name matches should have higher scores
    if name_match_scores and content_only_scores:
        avg_name_score = sum(name_match_scores) / len(name_match_scores)
        avg_content_score = sum(content_only_scores) / len(content_only_scores)
        assert (
            avg_name_score > avg_content_score
        ), "Name matches should score higher than content-only matches"


# ============================================================================
# Test 4: Typo Tolerance
# ============================================================================


def test_typo_tolerance(search_engine):
    """Test that search handles typos (2-3 character errors)."""
    # Test case 1: "flsk" should find "flask" (1 missing character)
    results_typo1 = search_engine.search("flsk")
    assert len(results_typo1) > 0, "Should find 'flask' with typo 'flsk'"

    # Check that Flask snippets are in results
    flask_found = any(
        "flask" in result["snippet"].name.lower() for result in results_typo1[:3]
    )
    assert flask_found, "Should find Flask snippets with typo 'flsk'"

    # Test case 2: "pythno" should find "python" (1 transposition)
    results_typo2 = search_engine.search("pythno")
    assert len(results_typo2) > 0, "Should find 'python' with typo 'pythno'"

    # Check that Python snippets are in results
    python_found = any(
        "python" in result["snippet"].name.lower()
        or any("python" in tag.lower() for tag in result["snippet"].tags)
        for result in results_typo2[:3]
    )
    assert python_found, "Should find Python snippets with typo 'pythno'"

    # Test case 3: "dokcer" should find "docker" (1 transposition)
    results_typo3 = search_engine.search("dokcer")
    assert len(results_typo3) > 0, "Should find 'docker' with typo 'dokcer'"

    # Check that Docker snippets are in results
    docker_found = any(
        "docker" in result["snippet"].name.lower()
        or any("docker" in tag.lower() for tag in result["snippet"].tags)
        for result in results_typo3[:3]
    )
    assert docker_found, "Should find Docker snippets with typo 'dokcer'"


# ============================================================================
# Test 5: Empty Query
# ============================================================================


def test_empty_query(search_engine):
    """Test that empty query returns empty list or all snippets (define behavior)."""
    # Decision: Empty query returns empty list (user must type to search)
    results_empty = search_engine.search("")
    assert isinstance(results_empty, list), "Empty query should return a list"
    assert len(results_empty) == 0, "Empty query should return empty list"

    # Test whitespace-only query
    results_whitespace = search_engine.search("   ")
    assert (
        len(results_whitespace) == 0
    ), "Whitespace-only query should return empty list"


# ============================================================================
# Test 6: No Results
# ============================================================================


def test_no_results(search_engine):
    """Test that nonsense query returns empty list gracefully."""
    # Search for gibberish that won't match anything
    results = search_engine.search("xyzabc123nonsense")

    assert isinstance(results, list), "No results should return a list"
    assert len(results) == 0, "Nonsense query should return empty list"

    # Verify no exception raised
    try:
        search_engine.search("qwertyuiopasdfghjkl")
        assert True, "No exception should be raised for no results"
    except Exception as e:
        pytest.fail(f"Exception raised for no results: {e}")


# ============================================================================
# Test 7: Performance Benchmark (200 snippets <100ms)
# ============================================================================


def test_performance_benchmark(tmpdir):
    """Test that searching 200 snippets completes in <100ms."""
    # Generate 200 test snippets
    import yaml
    from datetime import date

    large_snippets = {
        "version": 1,
        "snippets": [
            {
                "id": f"snippet-{i}",
                "name": f"Test Snippet {i}",
                "description": f"Description for snippet {i}",
                "content": f"Content of snippet {i} with some sample text",
                "tags": ["test", f"tag{i % 10}", "performance"],
                "created": str(date.today()),
                "modified": str(date.today()),
            }
            for i in range(200)
        ],
    }

    # Add some Flask and Python snippets for meaningful search
    large_snippets["snippets"].extend(
        [
            {
                "id": "flask-test-1",
                "name": "Flask application",
                "description": "Run Flask server",
                "content": "flask run --port 5000",
                "tags": ["flask", "python", "web"],
                "created": str(date.today()),
                "modified": str(date.today()),
            },
            {
                "id": "python-test-1",
                "name": "Python virtual environment",
                "description": "Create Python venv",
                "content": "python -m venv .venv",
                "tags": ["python", "venv"],
                "created": str(date.today()),
                "modified": str(date.today()),
            },
        ]
    )

    # Write to temporary file
    large_file = tmpdir / "large_snippets.yaml"
    with open(large_file, "w") as f:
        yaml.dump(large_snippets, f)

    # Load snippets
    manager = SnippetManager(str(large_file))
    snippets = manager.load()

    # Create search engine
    search_engine = SearchEngine(snippets)

    # Benchmark search
    start_time = time.perf_counter()
    results = search_engine.search("flask")
    elapsed_time = time.perf_counter() - start_time

    # Convert to milliseconds
    elapsed_ms = elapsed_time * 1000

    assert elapsed_ms < 100, f"Search took {elapsed_ms:.2f}ms, expected <100ms"
    assert len(results) > 0, "Should find Flask snippets in large library"

    print(f"\n✅ Performance: Searched 202 snippets in {elapsed_ms:.2f}ms")


# ============================================================================
# Test 8: Special Characters
# ============================================================================


def test_special_characters(search_engine):
    """Test that queries with special characters don't crash."""
    special_queries = [
        "email@test.com",
        "C:\\Users\\test",
        "regex.*pattern",
        "$(variable)",
        "100%",
        "A&B|C",
        "test/path",
        "[brackets]",
        "{braces}",
        "<angle>",
        "quotes\"test'",
    ]

    for query in special_queries:
        try:
            results = search_engine.search(query)
            assert isinstance(results, list), f"Query '{query}' should return a list"
        except Exception as e:
            pytest.fail(f"Exception raised for special character query '{query}': {e}")


# ============================================================================
# Test 9: Unicode Handling
# ============================================================================


def test_unicode_handling(search_engine):
    """Test that unicode in queries and snippets works correctly."""
    # Search for unicode content
    results_emoji = search_engine.search("🚀")
    # May or may not find results depending on fuzzy matching unicode
    assert isinstance(results_emoji, list), "Unicode emoji query should return a list"

    # Search for unicode text
    results_chinese = search_engine.search("世界")
    assert isinstance(
        results_chinese, list
    ), "Unicode Chinese query should return a list"

    # Search for accented characters
    results_accents = search_engine.search("éàü")
    assert isinstance(
        results_accents, list
    ), "Accented character query should return a list"

    # Verify no crashes with mixed unicode
    try:
        results_mixed = search_engine.search("test 🎉 unicode 中文")
        assert isinstance(
            results_mixed, list
        ), "Mixed unicode query should return a list"
    except Exception as e:
        pytest.fail(f"Exception raised for mixed unicode query: {e}")


# ============================================================================
# Test 10: Result Ranking
# ============================================================================


def test_result_ranking(search_engine):
    """Test that results are ordered by descending relevance score."""
    results = search_engine.search("powershell")

    assert len(results) > 0, "Should find PowerShell snippets"

    # Verify scores are in descending order
    scores = [result["score"] for result in results]

    for i in range(len(scores) - 1):
        assert (
            scores[i] >= scores[i + 1]
        ), f"Scores should be descending: {scores[i]} >= {scores[i+1]}"

    # Verify first result has highest score
    if len(results) >= 2:
        assert (
            results[0]["score"] >= results[1]["score"]
        ), "First result should have highest score"


# ============================================================================
# Additional Test: Threshold Filtering
# ============================================================================


def test_threshold_filtering(search_engine):
    """Test that results below threshold are filtered out."""
    # Search with very low threshold (should return many results)
    results_low_threshold = search_engine.search("test", threshold=10)

    # Search with high threshold (should return fewer results)
    results_high_threshold = search_engine.search("test", threshold=80)

    # High threshold should return fewer or equal results
    assert len(results_high_threshold) <= len(
        results_low_threshold
    ), "High threshold should return fewer results than low threshold"

    # All results should be above threshold
    for result in results_high_threshold:
        assert (
            result["score"] >= 80
        ), f"All results should have score >= 80, got {result['score']}"


# ============================================================================
# Additional Test: Case Insensitivity
# ============================================================================


def test_case_insensitivity(search_engine):
    """Test that search is case-insensitive."""
    results_lower = search_engine.search("flask")
    results_upper = search_engine.search("FLASK")
    results_mixed = search_engine.search("FlAsK")

    # All should return Flask-related results
    assert len(results_lower) > 0, "Lowercase query should return results"
    assert len(results_upper) > 0, "Uppercase query should return results"
    assert len(results_mixed) > 0, "Mixed case query should return results"

    # Should find similar results (scores may vary slightly due to fuzzy matching)
    flask_in_lower = any(
        "flask" in r["snippet"].name.lower() for r in results_lower[:3]
    )
    flask_in_upper = any(
        "flask" in r["snippet"].name.lower() for r in results_upper[:3]
    )
    flask_in_mixed = any(
        "flask" in r["snippet"].name.lower() for r in results_mixed[:3]
    )

    assert flask_in_lower, "Lowercase query should find Flask snippets"
    assert flask_in_upper, "Uppercase query should find Flask snippets"
    assert flask_in_mixed, "Mixed case query should find Flask snippets"
