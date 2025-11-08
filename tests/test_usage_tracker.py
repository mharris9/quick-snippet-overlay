"""
Tests for UsageTracker module

Tests usage tracking, persistence, and cleanup functionality.
"""

import pytest
import yaml
from pathlib import Path
from src.usage_tracker import UsageTracker


class TestUsageTrackerInitialization:
    """Test UsageTracker initialization and file creation."""

    def test_init_creates_empty_stats_if_file_missing(self, tmp_path):
        """UsageTracker should initialize with empty stats if file doesn't exist."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        # Should have empty stats
        assert tracker.get_count("snippet-1") == 0
        assert tracker.get_count("snippet-2") == 0

    def test_init_loads_existing_stats_file(self, tmp_path):
        """UsageTracker should load existing stats from file."""
        stats_file = tmp_path / "usage_stats.yaml"

        # Create stats file with data
        stats_data = {
            "snippet_usage": {
                "snippet-1": 42,
                "snippet-2": 15,
                "snippet-3": 8,
            }
        }
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        # Load tracker
        tracker = UsageTracker(str(stats_file))

        # Should have loaded stats
        assert tracker.get_count("snippet-1") == 42
        assert tracker.get_count("snippet-2") == 15
        assert tracker.get_count("snippet-3") == 8

    def test_init_handles_corrupted_stats_file(self, tmp_path):
        """UsageTracker should handle corrupted YAML gracefully."""
        stats_file = tmp_path / "usage_stats.yaml"

        # Create corrupted YAML file
        with open(stats_file, "w") as f:
            f.write("invalid: yaml: content: {{{\n")

        # Should not crash, should initialize with empty stats
        tracker = UsageTracker(str(stats_file))
        assert tracker.get_count("snippet-1") == 0

    def test_init_handles_invalid_stats_structure(self, tmp_path):
        """UsageTracker should handle invalid stats structure."""
        stats_file = tmp_path / "usage_stats.yaml"

        # Create file with wrong structure
        with open(stats_file, "w") as f:
            yaml.dump({"wrong_key": {"snippet-1": 10}}, f)

        # Should initialize with empty stats
        tracker = UsageTracker(str(stats_file))
        assert tracker.get_count("snippet-1") == 0


class TestUsageTrackerIncrement:
    """Test usage count increment functionality."""

    def test_increment_new_snippet(self, tmp_path):
        """Incrementing new snippet should set count to 1."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")

        assert tracker.get_count("snippet-1") == 1

    def test_increment_existing_snippet(self, tmp_path):
        """Incrementing existing snippet should increase count."""
        stats_file = tmp_path / "usage_stats.yaml"

        # Create stats with existing data
        stats_data = {"snippet_usage": {"snippet-1": 10}}
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))
        tracker.increment("snippet-1")

        assert tracker.get_count("snippet-1") == 11

    def test_increment_multiple_times(self, tmp_path):
        """Multiple increments should accumulate."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")
        tracker.increment("snippet-1")
        tracker.increment("snippet-1")

        assert tracker.get_count("snippet-1") == 3

    def test_increment_different_snippets(self, tmp_path):
        """Incrementing different snippets should track separately."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")
        tracker.increment("snippet-2")
        tracker.increment("snippet-1")

        assert tracker.get_count("snippet-1") == 2
        assert tracker.get_count("snippet-2") == 1


class TestUsageTrackerPersistence:
    """Test save and load functionality."""

    def test_save_creates_file(self, tmp_path):
        """Save should create stats file."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")
        tracker.save()

        # File should exist
        assert stats_file.exists()

    def test_save_writes_correct_format(self, tmp_path):
        """Save should write correct YAML format."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")
        tracker.increment("snippet-2")
        tracker.increment("snippet-1")
        tracker.save()

        # Load and verify format
        with open(stats_file, "r") as f:
            data = yaml.safe_load(f)

        assert "snippet_usage" in data
        assert data["snippet_usage"]["snippet-1"] == 2
        assert data["snippet_usage"]["snippet-2"] == 1

    def test_save_and_reload_preserves_data(self, tmp_path):
        """Saving and reloading should preserve usage data."""
        stats_file = tmp_path / "usage_stats.yaml"

        # First tracker: increment and save
        tracker1 = UsageTracker(str(stats_file))
        tracker1.increment("snippet-1")
        tracker1.increment("snippet-2")
        tracker1.increment("snippet-1")
        tracker1.save()

        # Second tracker: load from file
        tracker2 = UsageTracker(str(stats_file))

        assert tracker2.get_count("snippet-1") == 2
        assert tracker2.get_count("snippet-2") == 1

    def test_save_creates_parent_directory(self, tmp_path):
        """Save should create parent directory if missing."""
        stats_file = tmp_path / "subdir" / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")
        tracker.save()

        # Directory and file should exist
        assert stats_file.parent.exists()
        assert stats_file.exists()


class TestUsageTrackerCleanup:
    """Test cleanup of orphaned usage stats."""

    def test_cleanup_removes_orphaned_snippets(self, tmp_path):
        """Cleanup should remove stats for non-existent snippets."""
        stats_file = tmp_path / "usage_stats.yaml"

        # Create stats with some snippets
        stats_data = {
            "snippet_usage": {
                "snippet-1": 10,
                "snippet-2": 20,
                "snippet-3": 30,
                "snippet-4": 40,
            }
        }
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))

        # Cleanup: only snippet-1 and snippet-3 exist
        tracker.cleanup_orphaned(["snippet-1", "snippet-3"])

        # Orphaned snippets should be removed
        assert tracker.get_count("snippet-1") == 10
        assert tracker.get_count("snippet-2") == 0  # Removed
        assert tracker.get_count("snippet-3") == 30
        assert tracker.get_count("snippet-4") == 0  # Removed

    def test_cleanup_preserves_valid_snippets(self, tmp_path):
        """Cleanup should preserve stats for valid snippets."""
        stats_file = tmp_path / "usage_stats.yaml"

        stats_data = {
            "snippet_usage": {
                "snippet-1": 10,
                "snippet-2": 20,
            }
        }
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))

        # All snippets are valid
        tracker.cleanup_orphaned(["snippet-1", "snippet-2"])

        assert tracker.get_count("snippet-1") == 10
        assert tracker.get_count("snippet-2") == 20

    def test_cleanup_with_empty_valid_list(self, tmp_path):
        """Cleanup with empty valid list should remove all stats."""
        stats_file = tmp_path / "usage_stats.yaml"

        stats_data = {
            "snippet_usage": {
                "snippet-1": 10,
                "snippet-2": 20,
            }
        }
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))

        # No valid snippets
        tracker.cleanup_orphaned([])

        assert tracker.get_count("snippet-1") == 0
        assert tracker.get_count("snippet-2") == 0


class TestUsageTrackerGetCount:
    """Test get_count functionality."""

    def test_get_count_returns_zero_for_new_snippet(self, tmp_path):
        """get_count should return 0 for snippets that haven't been used."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        assert tracker.get_count("nonexistent-snippet") == 0

    def test_get_count_returns_correct_value(self, tmp_path):
        """get_count should return correct usage count."""
        stats_file = tmp_path / "usage_stats.yaml"

        stats_data = {"snippet_usage": {"snippet-1": 42}}
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))

        assert tracker.get_count("snippet-1") == 42


class TestUsageTrackerGetAllCounts:
    """Test get_all_counts functionality."""

    def test_get_all_counts_returns_empty_dict_initially(self, tmp_path):
        """get_all_counts should return empty dict for new tracker."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        assert tracker.get_all_counts() == {}

    def test_get_all_counts_returns_all_stats(self, tmp_path):
        """get_all_counts should return all usage statistics."""
        stats_file = tmp_path / "usage_stats.yaml"

        stats_data = {
            "snippet_usage": {
                "snippet-1": 42,
                "snippet-2": 15,
                "snippet-3": 8,
            }
        }
        with open(stats_file, "w") as f:
            yaml.dump(stats_data, f)

        tracker = UsageTracker(str(stats_file))

        all_counts = tracker.get_all_counts()
        assert all_counts == {
            "snippet-1": 42,
            "snippet-2": 15,
            "snippet-3": 8,
        }

    def test_get_all_counts_returns_copy_not_reference(self, tmp_path):
        """get_all_counts should return a copy, not internal reference."""
        stats_file = tmp_path / "usage_stats.yaml"
        tracker = UsageTracker(str(stats_file))

        tracker.increment("snippet-1")

        counts1 = tracker.get_all_counts()
        counts1["snippet-2"] = 999  # Modify returned dict

        counts2 = tracker.get_all_counts()
        assert "snippet-2" not in counts2  # Should not be affected
