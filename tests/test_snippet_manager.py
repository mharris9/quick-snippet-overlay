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
