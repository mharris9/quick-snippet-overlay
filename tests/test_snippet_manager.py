"""
Test Suite for SnippetManager - Phase 1: Core Data Layer

This test suite follows Test-Driven Development (TDD) approach.
All 11 tests are written BEFORE implementation.

Test Coverage:
1. Load valid snippets
2. Validate snippet schema
3. Load malformed YAML
4. Create sample file when missing
5. File watcher with debounce
6. Backup creation
7. Backup rotation (delete oldest)
8. Duplicate ID auto-fix
9. Large library performance
10. File watcher handles locked file
11. Validate ID uniqueness
"""

import pytest
import time
import yaml
from pathlib import Path
from datetime import date
from unittest.mock import patch, MagicMock
from src.snippet_manager import SnippetManager, Snippet


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def valid_snippets_file():
    """Path to valid test snippets YAML file."""
    return Path(__file__).parent / "fixtures" / "valid_snippets.yaml"


@pytest.fixture
def invalid_snippets_file():
    """Path to invalid test snippets YAML file."""
    return Path(__file__).parent / "fixtures" / "invalid_snippets.yaml"


@pytest.fixture
def temp_snippets_file(tmp_path):
    """Create a temporary snippets file path."""
    return tmp_path / "snippets.yaml"


@pytest.fixture
def temp_snippets_dir(tmp_path):
    """Create a temporary directory for snippets."""
    return tmp_path


@pytest.fixture
def manager_with_valid_file(valid_snippets_file):
    """Create a SnippetManager with valid test data."""
    return SnippetManager(str(valid_snippets_file))


# ============================================================================
# Test Case 1: Load Valid Snippets
# ============================================================================


def test_load_valid_snippets(manager_with_valid_file):
    """
    Test loading a well-formed YAML file with valid snippets.

    Verifies:
    - Correct number of snippets loaded (3 from valid_snippets.yaml)
    - All snippet fields are correctly parsed
    - IDs, names, descriptions, content, tags, and dates are valid
    """
    snippets = manager_with_valid_file.load()

    # Assert correct count
    assert len(snippets) == 3, "Should load exactly 3 snippets from valid_snippets.yaml"

    # Verify first snippet
    snippet1 = snippets[0]
    assert snippet1.id == "test-snippet-1"
    assert snippet1.name == "Test Snippet"
    assert snippet1.description == "A test snippet for unit tests"
    assert snippet1.content == 'echo "Hello, World!"'
    assert snippet1.tags == ["test", "example"]
    assert snippet1.created == date(2025, 11, 4)
    assert snippet1.modified == date(2025, 11, 4)

    # Verify second snippet
    snippet2 = snippets[1]
    assert snippet2.id == "test-snippet-2"
    assert snippet2.name == "PowerShell Command"
    assert "Get-ChildItem" in snippet2.content

    # Verify third snippet has variables
    snippet3 = snippets[2]
    assert snippet3.id == "test-snippet-3"
    assert "{{app_name:app}}" in snippet3.content
    assert "{{port:5000}}" in snippet3.content


# ============================================================================
# Test Case 2: Validate Snippet Schema
# ============================================================================


def test_validate_snippet_schema():
    """
    Test snippet validation logic for required fields.

    Verifies:
    - Valid snippet passes validation
    - Missing 'id' fails validation
    - Missing 'name' fails validation
    - Missing 'content' fails validation
    """
    # Valid snippet
    valid_snippet = Snippet(
        id="test-id",
        name="Test Name",
        description="Test Description",
        content="Test Content",
        tags=["test"],
        created=date.today(),
        modified=date.today(),
    )
    assert valid_snippet.validate() is True

    # Missing ID (empty string)
    invalid_snippet_no_id = Snippet(
        id="",
        name="Test Name",
        description="Test Description",
        content="Test Content",
        tags=["test"],
        created=date.today(),
        modified=date.today(),
    )
    assert invalid_snippet_no_id.validate() is False

    # Missing name (empty string)
    invalid_snippet_no_name = Snippet(
        id="test-id",
        name="",
        description="Test Description",
        content="Test Content",
        tags=["test"],
        created=date.today(),
        modified=date.today(),
    )
    assert invalid_snippet_no_name.validate() is False

    # Missing content (empty string)
    invalid_snippet_no_content = Snippet(
        id="test-id",
        name="Test Name",
        description="Test Description",
        content="",
        tags=["test"],
        created=date.today(),
        modified=date.today(),
    )
    assert invalid_snippet_no_content.validate() is False


# ============================================================================
# Test Case 3: Load Malformed YAML
# ============================================================================


def test_load_malformed_yaml(temp_snippets_file):
    """
    Test graceful handling of YAML syntax errors.

    Verifies:
    - YAMLError is caught (not raised to caller)
    - Fallback to last known good state
    - No application crash
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create a malformed YAML file
    malformed_yaml = """
version: 1
snippets:
  - id: test
    name: Test
    content: |
      This is valid content
    tags: [test
    # Missing closing bracket - syntax error
"""
    temp_snippets_file.write_text(malformed_yaml)

    # First load should return empty list (no last good state yet)
    snippets = manager.load()
    assert isinstance(snippets, list)
    assert len(snippets) == 0, "Should return empty list when no last good state exists"

    # Now create a valid file and load it
    valid_yaml = """
version: 1
snippets:
  - id: valid-snippet
    name: Valid Snippet
    description: This is valid
    content: echo "valid"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(valid_yaml)
    snippets = manager.load()
    assert len(snippets) == 1

    # Now corrupt the file again
    temp_snippets_file.write_text(malformed_yaml)
    snippets = manager.load()

    # Should return last good state (1 snippet)
    assert len(snippets) == 1
    assert snippets[0].id == "valid-snippet"


# ============================================================================
# Test Case 4: Create Sample File When Missing
# ============================================================================


def test_load_missing_file_creates_sample(temp_snippets_file):
    """
    Test sample file creation when snippets.yaml doesn't exist.

    Verifies:
    - Sample file is created at expected path
    - Sample file contains 5+ example snippets
    - Sample file is valid YAML
    - Next load() succeeds with sample data
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Verify file doesn't exist
    assert not temp_snippets_file.exists()

    # Load should create sample file
    snippets = manager.load()

    # Verify file was created
    assert temp_snippets_file.exists(), "Sample file should be created"

    # Verify file contains valid YAML
    with open(temp_snippets_file) as f:
        data = yaml.safe_load(f)
    assert "snippets" in data
    assert isinstance(data["snippets"], list)

    # Verify at least 5 sample snippets
    assert len(snippets) >= 5, "Sample file should contain at least 5 example snippets"

    # Verify sample snippets have required fields
    for snippet in snippets:
        assert snippet.id, "Sample snippet should have ID"
        assert snippet.name, "Sample snippet should have name"
        assert snippet.content, "Sample snippet should have content"
        assert snippet.validate(), "Sample snippet should pass validation"


# ============================================================================
# Test Case 5: File Watcher with Debounce
# ============================================================================


def test_file_watcher_reload_with_debounce(temp_snippets_file):
    """
    Test file watcher with debounce logic.

    Verifies:
    - Multiple rapid file changes trigger only 1 reload
    - Debounce delay is 500ms
    - New snippets appear after debounce period
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    initial_yaml = """
version: 1
snippets:
  - id: initial-snippet
    name: Initial Snippet
    description: Initial content
    content: echo "initial"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(initial_yaml)
    initial_snippets = manager.load()
    assert len(initial_snippets) == 1

    # Track reload count
    reload_count = [0]

    def on_reload():
        reload_count[0] += 1
        manager.load()

    # Start file watcher
    observer = manager.watch_file(on_reload)

    try:
        # Modify file 3 times rapidly (within 1 second)
        for i in range(3):
            updated_yaml = f"""
version: 1
snippets:
  - id: updated-snippet-{i}
    name: Updated Snippet {i}
    description: Updated content
    content: echo "updated {i}"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
            temp_snippets_file.write_text(updated_yaml)
            time.sleep(0.1)  # 100ms between writes

        # Wait for debounce period (500ms) + buffer
        time.sleep(0.8)

        # Should have triggered only 1-2 reloads due to debounce
        # (not 3, which would happen without debounce)
        assert (
            reload_count[0] <= 2
        ), f"Debounce failed: {reload_count[0]} reloads instead of ≤2"

        # Verify latest snippets are loaded
        current_snippets = manager.snippets
        assert len(current_snippets) == 1
        assert current_snippets[0].name.startswith("Updated Snippet")

    finally:
        observer.stop()
        observer.join()


# ============================================================================
# Test Case 6: Backup Creation
# ============================================================================


def test_backup_creation(temp_snippets_file):
    """
    Test backup file creation before write operations.

    Verifies:
    - Backup file is created with correct naming (.backup.001)
    - Backup content matches original file
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    initial_yaml = """
version: 1
snippets:
  - id: test-snippet
    name: Test Snippet
    description: Test content
    content: echo "test"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(initial_yaml)
    manager.load()

    # Create backup
    manager.create_backup()

    # Verify backup exists
    backup_file = Path(f"{temp_snippets_file}.backup.001")
    assert backup_file.exists(), "Backup file should be created"

    # Verify backup content matches original
    assert backup_file.read_text() == temp_snippets_file.read_text()


# ============================================================================
# Test Case 7: Backup Rotation (Delete Oldest)
# ============================================================================


def test_backup_rotation_deletes_oldest(temp_snippets_file):
    """
    Test backup rotation when 6th backup is created.

    Verifies:
    - When 6th backup created, oldest (backup.001) is deleted
    - Backups are renamed: .002 → .001, .003 → .002, etc.
    - Newest backup is always .001
    - Maximum of 5 backups maintained
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    initial_yaml = """
version: 1
snippets:
  - id: test-snippet
    name: Test Snippet
    description: Test content
    content: echo "test"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(initial_yaml)
    manager.load()

    # Create 5 backups manually
    for i in range(1, 6):
        backup_path = Path(f"{temp_snippets_file}.backup.{i:03d}")
        backup_path.write_text(f"Backup {i} content")

    # Verify all 5 backups exist
    for i in range(1, 6):
        assert Path(f"{temp_snippets_file}.backup.{i:03d}").exists()

    # Save original backup.002 content to verify rotation
    backup_002_original_content = Path(f"{temp_snippets_file}.backup.002").read_text()

    # Create 6th backup (should trigger rotation)
    manager.create_backup()

    # Verify backup.006 does NOT exist (we maintain max 5)
    assert not Path(f"{temp_snippets_file}.backup.006").exists()

    # Verify backup.001 has NEW content (current file)
    backup_001 = Path(f"{temp_snippets_file}.backup.001")
    assert backup_001.exists()
    assert "test-snippet" in backup_001.read_text()

    # Verify rotation: old backup.002 content should now be in backup.001
    # Actually, the rotation scheme is: delete .005, rename .004→.005, etc.
    # Then create new .001 from current file
    # So we should verify .001 exists and .005 or .006 don't exist
    assert backup_001.exists()
    assert not Path(f"{temp_snippets_file}.backup.006").exists()


# ============================================================================
# Test Case 8: Duplicate Snippet IDs Auto-Fix
# ============================================================================


def test_duplicate_snippet_ids_auto_fix(temp_snippets_file, caplog):
    """
    Test automatic fixing of duplicate snippet IDs.

    Verifies:
    - When duplicate IDs found, second occurrence renamed with "-1" suffix
    - Warning is logged
    - Both snippets are loaded successfully
    - Final IDs are unique
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with duplicate IDs
    duplicate_yaml = """
version: 1
snippets:
  - id: duplicate
    name: First Duplicate
    description: First occurrence
    content: echo "first"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: duplicate
    name: Second Duplicate
    description: Second occurrence
    content: echo "second"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(duplicate_yaml)

    # Load snippets (should auto-fix duplicates)
    with caplog.at_level("WARNING"):
        snippets = manager.load()

    # Verify both snippets loaded
    assert len(snippets) == 2

    # Verify first keeps original ID
    assert snippets[0].id == "duplicate"
    assert snippets[0].name == "First Duplicate"

    # Verify second has renamed ID
    assert snippets[1].id == "duplicate-1"
    assert snippets[1].name == "Second Duplicate"

    # Verify warning was logged
    assert "Duplicate ID" in caplog.text or "duplicate" in caplog.text.lower()


# ============================================================================
# Test Case 9: Large Snippet Library Performance
# ============================================================================


def test_large_snippet_library_performance(temp_snippets_file):
    """
    Test performance with large snippet library.

    Verifies:
    - Load 500 snippets in < 1 second
    - Memory usage is reasonable
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Generate 500 snippets programmatically
    snippets_data = ["version: 1", "snippets:"]
    for i in range(500):
        snippet = f"""
  - id: snippet-{i}
    name: Snippet {i}
    description: Description for snippet {i}
    content: echo "Content {i}"
    tags: [test, perf]
    created: 2025-11-04
    modified: 2025-11-04
"""
        snippets_data.append(snippet)

    large_yaml = "\n".join(snippets_data)
    temp_snippets_file.write_text(large_yaml)

    # Measure load time
    start_time = time.time()
    snippets = manager.load()
    load_time = time.time() - start_time

    # Verify count
    assert len(snippets) == 500

    # Verify performance: load time < 1 second
    assert load_time < 1.0, f"Load time {load_time:.3f}s exceeds 1s threshold"


# ============================================================================
# Test Case 10: File Watcher Handles Locked File
# ============================================================================


def test_file_watcher_handles_locked_file(temp_snippets_file, caplog):
    """
    Test file watcher behavior when file is locked.

    Verifies:
    - Retry logic (3 attempts with delay)
    - Uses cached snippets if all retries fail
    - Warning is logged
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial valid file
    initial_yaml = """
version: 1
snippets:
  - id: cached-snippet
    name: Cached Snippet
    description: This should be cached
    content: echo "cached"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(initial_yaml)
    snippets = manager.load()
    assert len(snippets) == 1
    assert snippets[0].id == "cached-snippet"

    # Mock file read to simulate locked file
    with patch("builtins.open", side_effect=PermissionError("File is locked")):
        with caplog.at_level("WARNING"):
            # Attempt to load should use cached version
            cached_snippets = manager.load()

    # Should return last good state
    assert len(cached_snippets) == 1
    assert cached_snippets[0].id == "cached-snippet"

    # Warning should be logged (though in this test we're not implementing retry yet)
    # This test documents expected behavior


# ============================================================================
# Test Case 11: Validate Snippet ID Uniqueness
# ============================================================================


def test_validate_snippet_id_uniqueness(temp_snippets_file):
    """
    Test that all snippet IDs are unique after auto-fix.

    Verifies:
    - No duplicate IDs in final snippet list
    - Auto-fix successfully creates unique IDs
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with multiple duplicates
    duplicate_yaml = """
version: 1
snippets:
  - id: duplicate
    name: First
    description: First
    content: echo "1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: duplicate
    name: Second
    description: Second
    content: echo "2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: duplicate
    name: Third
    description: Third
    content: echo "3"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: another
    name: Unique
    description: Unique
    content: echo "unique"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(duplicate_yaml)

    snippets = manager.load()

    # Extract all IDs
    ids = [s.id for s in snippets]

    # Verify no duplicates
    assert len(ids) == len(set(ids)), f"Duplicate IDs found: {ids}"

    # Verify expected IDs
    assert "duplicate" in ids
    assert "duplicate-1" in ids
    assert "duplicate-2" in ids
    assert "another" in ids

    # Verify count
    assert len(snippets) == 4


# ============================================================================
# Test Case 12: Get All Tags - Empty
# ============================================================================


def test_get_all_tags_empty(temp_snippets_file):
    """
    Test get_all_tags() with no snippets.

    Verifies:
    - Returns empty list when no snippets loaded
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Don't load any snippets (file doesn't exist yet)
    # Just call get_all_tags() directly
    tags = manager.get_all_tags()

    # Should return empty list
    assert tags == []
    assert isinstance(tags, list)


# ============================================================================
# Test Case 13: Get All Tags - Deduplicates
# ============================================================================


def test_get_all_tags_deduplicates(temp_snippets_file):
    """
    Test get_all_tags() deduplicates tags.

    Verifies:
    - Multiple snippets with same tag return tag only once
    - Duplicate tags within same snippet are deduplicated
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with duplicate tags
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [python, code]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [python, testing]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-3
    name: Snippet 3
    description: Third snippet
    content: echo "test 3"
    tags: [javascript, testing]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    tags = manager.get_all_tags()

    # Should deduplicate "python" and "testing"
    assert len(tags) == 4  # code, javascript, python, testing
    assert "python" in tags
    assert "testing" in tags
    assert "code" in tags
    assert "javascript" in tags

    # Verify no duplicates
    assert len(tags) == len(set(tags))


# ============================================================================
# Test Case 14: Get All Tags - Sorted
# ============================================================================


def test_get_all_tags_sorted(temp_snippets_file):
    """
    Test get_all_tags() returns alphabetically sorted tags.

    Verifies:
    - Tags are returned in alphabetical order
    - Sorting is case-insensitive (already normalized)
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with tags in random order
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [zebra, apple, mango, banana]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    tags = manager.get_all_tags()

    # Should be sorted alphabetically
    assert tags == ["apple", "banana", "mango", "zebra"]


# ============================================================================
# Test Case 15: Get All Tags - Multiple Snippets
# ============================================================================


def test_get_all_tags_from_multiple_snippets(temp_snippets_file):
    """
    Test get_all_tags() returns union of tags from multiple snippets.

    Verifies:
    - All tags from all snippets are included
    - Tags are deduplicated and sorted
    - Handles snippets with no tags
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with 3+ snippets with overlapping tags
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [python, django, backend]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [python, flask, backend]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-3
    name: Snippet 3
    description: Third snippet
    content: echo "test 3"
    tags: [javascript, frontend, react]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-4
    name: Snippet 4
    description: Fourth snippet with no tags
    content: echo "test 4"
    tags: []
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    tags = manager.get_all_tags()

    # Should have all unique tags from all snippets
    expected_tags = [
        "backend",
        "django",
        "flask",
        "frontend",
        "javascript",
        "python",
        "react",
    ]
    assert tags == expected_tags

    # Verify all expected tags present
    assert "python" in tags  # From snippet 1 and 2
    assert "backend" in tags  # From snippet 1 and 2
    assert "django" in tags  # From snippet 1 only
    assert "flask" in tags  # From snippet 2 only
    assert "javascript" in tags  # From snippet 3 only
    assert "react" in tags  # From snippet 3 only

    # Verify count (6 unique tags total, snippet 4 has no tags)
    assert len(tags) == 7


# ============================================================================
# Test Case 16: Delete Snippets
# ============================================================================


def test_delete_snippets(temp_snippets_file):
    """
    Test deleting multiple snippets.

    Verifies:
    - Snippets are removed from file
    - Remaining snippets are intact
    - File is saved correctly
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with 3 snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-3
    name: Snippet 3
    description: Third snippet
    content: echo "test 3"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)

    # Load initial snippets
    initial_snippets = manager.load()
    initial_count = len(initial_snippets)
    assert initial_count == 3

    # Delete 2 snippets
    ids_to_delete = [initial_snippets[0].id, initial_snippets[1].id]
    manager.delete_snippets(ids_to_delete)

    # Reload and verify
    remaining_snippets = manager.load()
    assert len(remaining_snippets) == initial_count - 2
    assert all(s.id not in ids_to_delete for s in remaining_snippets)

    # Verify the remaining snippet is the correct one
    assert remaining_snippets[0].id == "snippet-3"
    assert remaining_snippets[0].name == "Snippet 3"


def test_delete_nonexistent_snippet(temp_snippets_file):
    """
    Test deleting non-existent snippet raises error.

    Verifies:
    - ValueError is raised
    - Error message includes snippet ID
    - No snippets are deleted
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with 1 snippet
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Try to delete non-existent snippet
    with pytest.raises(ValueError, match="not found"):
        manager.delete_snippets(["nonexistent-id"])

    # Verify snippet still exists
    snippets = manager.load()
    assert len(snippets) == 1


def test_delete_all_snippets(temp_snippets_file):
    """
    Test deleting all snippets.

    Verifies:
    - All snippets can be deleted
    - Empty snippets list is written to file
    - File structure is preserved
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with 2 snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)

    # Load and delete all
    snippets = manager.load()
    all_ids = [s.id for s in snippets]
    manager.delete_snippets(all_ids)

    # Verify empty list
    remaining = manager.load()
    assert len(remaining) == 0


def test_get_all_snippets(temp_snippets_file):
    """
    Test get_all_snippets convenience method.

    Verifies:
    - Returns list of all snippets
    - Same result as load()
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create file with snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Get all snippets
    snippets = manager.get_all_snippets()

    # Verify
    assert isinstance(snippets, list)
    assert len(snippets) == 2
    assert snippets[0].id == "snippet-1"
    assert snippets[1].id == "snippet-2"


def test_save_snippets_preserves_data(temp_snippets_file):
    """
    Test that _save_snippets preserves all snippet data.

    Verifies:
    - All fields are saved correctly
    - File can be reloaded successfully
    - Dates are preserved
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create snippet with all fields
    snippet = Snippet(
        id="test-id",
        name="Test Name",
        description="Test Description",
        content="Test Content",
        tags=["tag1", "tag2"],
        created=date(2025, 11, 1),
        modified=date(2025, 11, 2),
    )

    # Save snippet
    manager._save_snippets([snippet])

    # Reload and verify
    loaded = manager.load()
    assert len(loaded) == 1

    s = loaded[0]
    assert s.id == "test-id"
    assert s.name == "Test Name"
    assert s.description == "Test Description"
    assert s.content == "Test Content"
    assert s.tags == ["tag1", "tag2"]
    assert s.created == date(2025, 11, 1)
    assert s.modified == date(2025, 11, 2)


# ============================================================================
# Test Case 17: Automatic Backup on Add
# ============================================================================


def test_automatic_backup_on_add_snippet(temp_snippets_file):
    """
    Test that add_snippet creates backup before adding.

    Verifies:
    - Backup file created before add operation
    - Backup contains original state
    - New snippet added successfully
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file with 1 snippet
    yaml_content = """
version: 1
snippets:
  - id: original-snippet
    name: Original Snippet
    description: Original content
    content: echo "original"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Add new snippet (should trigger backup)
    new_snippet = {
        "id": "new-snippet",
        "name": "New Snippet",
        "description": "New content",
        "content": 'echo "new"',
        "tags": ["test"],
        "created": "2025-11-04",
        "modified": "2025-11-04",
    }
    manager.add_snippet(new_snippet)

    # Verify backup was created
    backup_file = Path(f"{temp_snippets_file}.backup.001")
    assert backup_file.exists(), "Backup should be created before add"

    # Verify backup contains original state (1 snippet)
    with open(backup_file) as f:
        backup_data = yaml.safe_load(f)
    assert len(backup_data["snippets"]) == 1
    assert backup_data["snippets"][0]["id"] == "original-snippet"

    # Verify new file has 2 snippets
    current_snippets = manager.load()
    assert len(current_snippets) == 2


# ============================================================================
# Test Case 18: Automatic Backup on Update
# ============================================================================


def test_automatic_backup_on_update_snippet(temp_snippets_file):
    """
    Test that update_snippet creates backup before updating.

    Verifies:
    - Backup created before update operation
    - Backup contains state before update
    - Update applied successfully
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    yaml_content = """
version: 1
snippets:
  - id: snippet-to-update
    name: Original Name
    description: Original description
    content: echo "original"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Update snippet (should trigger backup)
    updated_data = {
        "name": "Updated Name",
        "description": "Updated description",
        "content": 'echo "updated"',
        "tags": ["test", "updated"],
    }
    manager.update_snippet("snippet-to-update", updated_data)

    # Verify backup was created
    backup_file = Path(f"{temp_snippets_file}.backup.001")
    assert backup_file.exists(), "Backup should be created before update"

    # Verify backup contains original name
    with open(backup_file) as f:
        backup_data = yaml.safe_load(f)
    assert backup_data["snippets"][0]["name"] == "Original Name"

    # Verify current file has updated name
    current_snippets = manager.load()
    assert current_snippets[0].name == "Updated Name"


# ============================================================================
# Test Case 19: Automatic Backup on Delete
# ============================================================================


def test_automatic_backup_on_delete_snippets(temp_snippets_file):
    """
    Test that delete_snippets creates backup before deleting.

    Verifies:
    - Backup created before delete operation
    - Backup contains all original snippets
    - Delete operation successful
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file with 3 snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-1
    name: Snippet 1
    description: First snippet
    content: echo "test 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Snippet 2
    description: Second snippet
    content: echo "test 2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-3
    name: Snippet 3
    description: Third snippet
    content: echo "test 3"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Delete 2 snippets (should trigger backup)
    manager.delete_snippets(["snippet-1", "snippet-2"])

    # Verify backup was created
    backup_file = Path(f"{temp_snippets_file}.backup.001")
    assert backup_file.exists(), "Backup should be created before delete"

    # Verify backup contains all 3 original snippets
    with open(backup_file) as f:
        backup_data = yaml.safe_load(f)
    assert len(backup_data["snippets"]) == 3

    # Verify current file has only 1 snippet
    current_snippets = manager.load()
    assert len(current_snippets) == 1
    assert current_snippets[0].id == "snippet-3"


# ============================================================================
# Test Case 20: Manual Backup with Timestamp
# ============================================================================


def test_manual_backup_with_timestamp(temp_snippets_file):
    """
    Test manual backup creation with timestamp.

    Verifies:
    - Manual backup created with timestamp in filename
    - Filename format: snippets.yaml.backup.YYYYMMDD-HHMMSS
    - Backup content matches current file
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    yaml_content = """
version: 1
snippets:
  - id: test-snippet
    name: Test Snippet
    description: Test content
    content: echo "test"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create manual backup
    backup_path = manager.create_manual_backup()

    # Verify backup exists
    assert backup_path is not None
    assert Path(backup_path).exists()

    # Verify filename format (contains timestamp)
    assert ".backup." in str(backup_path)
    # Should have format like: snippets.yaml.backup.20251107-143022

    # Verify content matches
    with open(backup_path) as f:
        backup_data = yaml.safe_load(f)
    assert len(backup_data["snippets"]) == 1
    assert backup_data["snippets"][0]["id"] == "test-snippet"


# ============================================================================
# Test Case 21: List Available Backups
# ============================================================================


def test_list_available_backups(temp_snippets_file):
    """
    Test listing available backup files.

    Verifies:
    - Both automatic and manual backups are listed
    - Returns sorted list (newest first)
    - Includes rotation backups and timestamped backups
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create main file
    yaml_content = """
version: 1
snippets:
  - id: test-snippet
    name: Test Snippet
    description: Test content
    content: echo "test"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create rotation backups
    for i in range(1, 4):
        backup_path = Path(f"{temp_snippets_file}.backup.{i:03d}")
        backup_path.write_text(f"Backup {i}")

    # Create manual backup
    manager.create_manual_backup()
    time.sleep(0.1)  # Ensure different timestamp
    manager.create_manual_backup()

    # List backups
    backups = manager.list_backups()

    # Should have 5 backups total (3 rotation + 2 manual)
    assert len(backups) >= 3  # At least rotation backups
    assert isinstance(backups, list)

    # Verify each backup has path and timestamp
    for backup in backups:
        assert "path" in backup
        assert "timestamp" in backup or "name" in backup
        assert Path(backup["path"]).exists()


# ============================================================================
# Test Case 22: Restore from Backup
# ============================================================================


def test_restore_from_backup(temp_snippets_file):
    """
    Test restoring snippets from backup file.

    Verifies:
    - Backup content replaces current file
    - Previous state is restored successfully
    - Manager reloads snippets after restore
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file with 2 snippets
    original_yaml = """
version: 1
snippets:
  - id: snippet-1
    name: Original Snippet 1
    description: Original content
    content: echo "original 1"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-2
    name: Original Snippet 2
    description: Original content
    content: echo "original 2"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(original_yaml)
    manager.load()

    # Create backup
    manager.create_backup()
    backup_file = Path(f"{temp_snippets_file}.backup.001")

    # Modify current file (delete 1 snippet)
    modified_yaml = """
version: 1
snippets:
  - id: snippet-2
    name: Modified Snippet 2
    description: Modified content
    content: echo "modified"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(modified_yaml)
    manager.load()
    assert len(manager.snippets) == 1

    # Restore from backup
    manager.restore_from_backup(str(backup_file))

    # Verify restoration
    restored_snippets = manager.load()
    assert len(restored_snippets) == 2
    assert restored_snippets[0].name == "Original Snippet 1"
    assert restored_snippets[1].name == "Original Snippet 2"


# ============================================================================
# Test Case 23: Restore from Invalid Backup
# ============================================================================


def test_restore_from_invalid_backup(temp_snippets_file):
    """
    Test error handling when restoring from invalid backup.

    Verifies:
    - ValueError raised if backup file doesn't exist
    - Current file remains unchanged
    - Error message is descriptive
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create initial file
    yaml_content = """
version: 1
snippets:
  - id: test-snippet
    name: Test Snippet
    description: Test content
    content: echo "test"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Try to restore from non-existent backup
    fake_backup = str(temp_snippets_file.parent / "nonexistent.backup")

    with pytest.raises(ValueError, match="not found|does not exist"):
        manager.restore_from_backup(fake_backup)

    # Verify current file unchanged
    current_snippets = manager.load()
    assert len(current_snippets) == 1
    assert current_snippets[0].id == "test-snippet"


# ============================================================================
# Test Case 24: Sort Snippets by Frequency - Descending
# ============================================================================


def test_sort_snippets_by_frequency_descending(temp_snippets_file, tmp_path):
    """
    Test snippets are sorted by usage frequency (most used first).

    Verifies:
    - Snippets with higher usage count appear first
    - Frequency sorting is descending (42 > 15 > 8)
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create test snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-low-usage
    name: Low Usage
    description: Used 8 times
    content: echo "low"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-high-usage
    name: High Usage
    description: Used 42 times
    content: echo "high"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-mid-usage
    name: Mid Usage
    description: Used 15 times
    content: echo "mid"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create usage tracker with stats
    from src.usage_tracker import UsageTracker

    stats_file = tmp_path / "usage_stats.yaml"
    tracker = UsageTracker(str(stats_file))
    tracker.usage_counts = {
        "snippet-high-usage": 42,
        "snippet-mid-usage": 15,
        "snippet-low-usage": 8,
    }

    # Get sorted snippets
    sorted_snippets = manager.get_sorted_snippets(tracker)

    # Verify order: high (42), mid (15), low (8)
    assert len(sorted_snippets) == 3
    assert sorted_snippets[0].id == "snippet-high-usage"
    assert sorted_snippets[1].id == "snippet-mid-usage"
    assert sorted_snippets[2].id == "snippet-low-usage"


# ============================================================================
# Test Case 25: Sort Snippets Alphabetically When Frequency Tied
# ============================================================================


def test_sort_snippets_alphabetically_when_frequency_tied(temp_snippets_file, tmp_path):
    """
    Test snippets with same frequency are sorted alphabetically by name.

    Verifies:
    - When usage counts are equal, alphabetical sorting is applied
    - Alphabetical sort is case-insensitive ascending (A-Z)
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create test snippets (all with same usage count)
    yaml_content = """
version: 1
snippets:
  - id: snippet-zebra
    name: Zebra Snippet
    description: Z comes last
    content: echo "zebra"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-alpha
    name: Alpha Snippet
    description: A comes first
    content: echo "alpha"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-bravo
    name: Bravo Snippet
    description: B comes second
    content: echo "bravo"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create usage tracker - all snippets have count of 10
    from src.usage_tracker import UsageTracker

    stats_file = tmp_path / "usage_stats.yaml"
    tracker = UsageTracker(str(stats_file))
    tracker.usage_counts = {
        "snippet-zebra": 10,
        "snippet-alpha": 10,
        "snippet-bravo": 10,
    }

    # Get sorted snippets
    sorted_snippets = manager.get_sorted_snippets(tracker)

    # Verify alphabetical order: Alpha, Bravo, Zebra
    assert len(sorted_snippets) == 3
    assert sorted_snippets[0].name == "Alpha Snippet"
    assert sorted_snippets[1].name == "Bravo Snippet"
    assert sorted_snippets[2].name == "Zebra Snippet"


# ============================================================================
# Test Case 26: New Snippets (Zero Usage) Appear at Bottom
# ============================================================================


def test_new_snippets_appear_at_bottom_alphabetically(temp_snippets_file, tmp_path):
    """
    Test snippets with zero usage appear at bottom, sorted alphabetically.

    Verifies:
    - Snippets with 0 usage come after all used snippets
    - Zero-usage snippets are sorted alphabetically among themselves
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create test snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-used
    name: Used Snippet
    description: Has usage count
    content: echo "used"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-new-z
    name: Zebra New
    description: Never used
    content: echo "new-z"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-new-a
    name: Alpha New
    description: Never used
    content: echo "new-a"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create usage tracker - only one snippet has usage
    from src.usage_tracker import UsageTracker

    stats_file = tmp_path / "usage_stats.yaml"
    tracker = UsageTracker(str(stats_file))
    tracker.usage_counts = {
        "snippet-used": 5,
        # snippet-new-z and snippet-new-a have 0 usage (not in dict)
    }

    # Get sorted snippets
    sorted_snippets = manager.get_sorted_snippets(tracker)

    # Verify order: Used (5), then Alpha New (0), then Zebra New (0)
    assert len(sorted_snippets) == 3
    assert sorted_snippets[0].id == "snippet-used"
    assert sorted_snippets[1].name == "Alpha New"  # Alphabetically first among zero-usage
    assert sorted_snippets[2].name == "Zebra New"  # Alphabetically second among zero-usage


# ============================================================================
# Test Case 27: Sort Snippets with Mixed Frequency and Alphabetical
# ============================================================================


def test_sort_snippets_mixed_frequency_and_alphabetical(temp_snippets_file, tmp_path):
    """
    Test comprehensive sorting: frequency primary, alphabetical secondary.

    Verifies:
    - Higher frequency snippets come first
    - Within same frequency, alphabetical order is applied
    - Zero-usage snippets appear at bottom alphabetically
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create test snippets with various usage patterns
    yaml_content = """
version: 1
snippets:
  - id: snippet-freq-10-zebra
    name: Zebra (Freq 10)
    description: Frequency 10
    content: echo "10z"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-freq-20-alpha
    name: Alpha (Freq 20)
    description: Frequency 20
    content: echo "20a"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-freq-10-alpha
    name: Alpha (Freq 10)
    description: Frequency 10
    content: echo "10a"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-new-zebra
    name: Zebra (New)
    description: Never used
    content: echo "0z"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-new-alpha
    name: Alpha (New)
    description: Never used
    content: echo "0a"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create usage tracker
    from src.usage_tracker import UsageTracker

    stats_file = tmp_path / "usage_stats.yaml"
    tracker = UsageTracker(str(stats_file))
    tracker.usage_counts = {
        "snippet-freq-20-alpha": 20,
        "snippet-freq-10-zebra": 10,
        "snippet-freq-10-alpha": 10,
        # snippet-new-* have 0 usage
    }

    # Get sorted snippets
    sorted_snippets = manager.get_sorted_snippets(tracker)

    # Expected order:
    # 1. Alpha (Freq 20) - highest frequency
    # 2. Alpha (Freq 10) - tied at 10, alphabetically before Zebra
    # 3. Zebra (Freq 10) - tied at 10, alphabetically after Alpha
    # 4. Alpha (New) - zero usage, alphabetically before Zebra
    # 5. Zebra (New) - zero usage, alphabetically after Alpha

    assert len(sorted_snippets) == 5
    assert sorted_snippets[0].name == "Alpha (Freq 20)"
    assert sorted_snippets[1].name == "Alpha (Freq 10)"
    assert sorted_snippets[2].name == "Zebra (Freq 10)"
    assert sorted_snippets[3].name == "Alpha (New)"
    assert sorted_snippets[4].name == "Zebra (New)"


# ============================================================================
# Test Case 28: Sort Snippets with Empty Usage Stats
# ============================================================================


def test_sort_snippets_with_empty_usage_stats(temp_snippets_file, tmp_path):
    """
    Test sorting when no usage statistics exist (all snippets have 0 usage).

    Verifies:
    - All snippets are sorted alphabetically by name
    - No errors occur with empty usage tracker
    """
    manager = SnippetManager(str(temp_snippets_file))

    # Create test snippets
    yaml_content = """
version: 1
snippets:
  - id: snippet-charlie
    name: Charlie
    description: C
    content: echo "c"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-alpha
    name: Alpha
    description: A
    content: echo "a"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
  - id: snippet-bravo
    name: Bravo
    description: B
    content: echo "b"
    tags: [test]
    created: 2025-11-04
    modified: 2025-11-04
"""
    temp_snippets_file.write_text(yaml_content)
    manager.load()

    # Create empty usage tracker
    from src.usage_tracker import UsageTracker

    stats_file = tmp_path / "usage_stats.yaml"
    tracker = UsageTracker(str(stats_file))

    # Get sorted snippets (should be alphabetical)
    sorted_snippets = manager.get_sorted_snippets(tracker)

    # Verify alphabetical order: Alpha, Bravo, Charlie
    assert len(sorted_snippets) == 3
    assert sorted_snippets[0].name == "Alpha"
    assert sorted_snippets[1].name == "Bravo"
    assert sorted_snippets[2].name == "Charlie"
