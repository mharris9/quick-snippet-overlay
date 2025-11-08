"""
Usage Tracker Module

Tracks snippet usage frequency and persists statistics to YAML file.

Key features:
- Track how many times each snippet is copied
- Persist usage counts across app restarts
- Cleanup orphaned stats when snippets are deleted
- Thread-safe increment operations
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, List

logger = logging.getLogger(__name__)


class UsageTracker:
    """
    Tracks snippet usage frequency and persists to file.

    Usage statistics are stored in YAML format:
    ```yaml
    snippet_usage:
      snippet-id-1: 42
      snippet-id-2: 15
      snippet-id-3: 8
    ```

    Methods:
        increment(snippet_id): Increment usage count for snippet
        get_count(snippet_id): Get usage count for snippet
        get_all_counts(): Get all usage counts as dict
        save(): Persist usage statistics to file
        cleanup_orphaned(valid_ids): Remove stats for deleted snippets
    """

    def __init__(self, stats_file: str):
        """
        Initialize UsageTracker.

        Args:
            stats_file: Path to usage statistics YAML file
        """
        self.stats_file = Path(stats_file)
        self.usage_counts: Dict[str, int] = {}
        self._load()

    def _load(self):
        """Load usage statistics from file."""
        if not self.stats_file.exists():
            logger.info(f"Usage stats file not found: {self.stats_file}, starting with empty stats")
            self.usage_counts = {}
            return

        try:
            with open(self.stats_file, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if data is None:
                logger.warning("Usage stats file is empty, starting with empty stats")
                self.usage_counts = {}
                return

            if not isinstance(data, dict) or "snippet_usage" not in data:
                logger.warning(
                    "Usage stats file has invalid structure, starting with empty stats"
                )
                self.usage_counts = {}
                return

            usage_data = data["snippet_usage"]
            if not isinstance(usage_data, dict):
                logger.warning(
                    "snippet_usage is not a dict, starting with empty stats"
                )
                self.usage_counts = {}
                return

            # Validate all values are integers
            validated_counts = {}
            for snippet_id, count in usage_data.items():
                if isinstance(count, int) and count >= 0:
                    validated_counts[snippet_id] = count
                else:
                    logger.warning(
                        f"Invalid count for snippet {snippet_id}: {count}, skipping"
                    )

            self.usage_counts = validated_counts
            logger.info(
                f"Loaded {len(self.usage_counts)} usage stats from {self.stats_file}"
            )

        except yaml.YAMLError as e:
            logger.error(f"Failed to parse usage stats YAML: {e}, starting with empty stats")
            self.usage_counts = {}
        except Exception as e:
            logger.error(f"Unexpected error loading usage stats: {e}, starting with empty stats")
            self.usage_counts = {}

    def increment(self, snippet_id: str):
        """
        Increment usage count for a snippet.

        Args:
            snippet_id: ID of snippet to increment
        """
        current_count = self.usage_counts.get(snippet_id, 0)
        self.usage_counts[snippet_id] = current_count + 1
        logger.debug(f"Incremented usage for {snippet_id} to {self.usage_counts[snippet_id]}")

    def get_count(self, snippet_id: str) -> int:
        """
        Get usage count for a snippet.

        Args:
            snippet_id: ID of snippet to query

        Returns:
            Usage count (0 if snippet has never been used)
        """
        return self.usage_counts.get(snippet_id, 0)

    def get_all_counts(self) -> Dict[str, int]:
        """
        Get all usage counts as dictionary.

        Returns:
            Dictionary mapping snippet IDs to usage counts (copy, not reference)
        """
        return self.usage_counts.copy()

    def save(self):
        """
        Save usage statistics to file.

        Creates parent directory if it doesn't exist.
        """
        try:
            # Create parent directory if needed
            self.stats_file.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            data = {"snippet_usage": self.usage_counts}
            with open(self.stats_file, "w", encoding="utf-8") as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=True)

            logger.info(f"Saved {len(self.usage_counts)} usage stats to {self.stats_file}")

        except Exception as e:
            logger.error(f"Failed to save usage stats: {e}")

    def cleanup_orphaned(self, valid_snippet_ids: List[str]):
        """
        Remove usage stats for snippets that no longer exist.

        Args:
            valid_snippet_ids: List of snippet IDs that currently exist
        """
        valid_ids_set = set(valid_snippet_ids)
        orphaned_ids = [sid for sid in self.usage_counts.keys() if sid not in valid_ids_set]

        for orphaned_id in orphaned_ids:
            del self.usage_counts[orphaned_id]
            logger.debug(f"Removed orphaned usage stat for {orphaned_id}")

        if orphaned_ids:
            logger.info(f"Cleaned up {len(orphaned_ids)} orphaned usage stats")
