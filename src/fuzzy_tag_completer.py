"""
FuzzyTagCompleter - Custom QCompleter with fuzzy matching for tag suggestions.

This module provides a QCompleter subclass that uses rapidfuzz for typo-tolerant
tag autocomplete in the snippet editor dialog.
"""

from PySide6.QtWidgets import QCompleter
from PySide6.QtCore import Qt, QStringListModel
from rapidfuzz import fuzz
from typing import List


class FuzzyTagCompleter(QCompleter):
    """Custom QCompleter with fuzzy matching for tag suggestions."""

    def __init__(self, tags: List[str], parent=None):
        """
        Initialize fuzzy tag completer.

        Args:
            tags: List of existing tags to suggest
            parent: Parent widget (optional)
        """
        super().__init__(tags, parent)
        self.tags = tags
        self.score_cutoff = (
            40  # Lower threshold for autocomplete (more lenient than search)
        )
        self.current_prefix = None  # For multi-tag support

        # Configure base completer
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.PopupCompletion)

    def splitPath(self, path: str) -> List[str]:
        """
        Override to provide fuzzy-matched suggestions.

        Qt calls this method to determine what suggestions to show.
        We use rapidfuzz to find tags that match the input with typo tolerance.

        For multi-tag support: If current_prefix is set, use it instead of path.
        This allows comma-separated tags to get independent suggestions.

        Args:
            path: Current input text (may be full text or current tag)

        Returns:
            List of matching tags (fuzzy sorted by score)
        """
        # Use current_prefix if set (for multi-tag support)
        # Otherwise use path (for backward compatibility)
        match_text = self.current_prefix if self.current_prefix is not None else path

        if not match_text:
            # Show all tags if no input
            return self.tags[:10]

        # Get fuzzy matches with scores
        matches = []
        match_lower = match_text.lower().strip()

        for tag in self.tags:
            tag_lower = tag.lower()

            # Boost score for exact prefix matches
            if tag_lower.startswith(match_lower):
                score = 100  # Perfect prefix match
            else:
                # Use partial_ratio for fuzzy matching (e.g., typos)
                score = fuzz.partial_ratio(match_lower, tag_lower)

            if score >= self.score_cutoff:
                matches.append((tag, score))

        # Sort by score (descending), then alphabetically
        matches.sort(key=lambda x: (-x[1], x[0]))

        # Return top 10 matches (limit suggestions)
        result = [tag for tag, score in matches[:10]]

        # Always return at least something to keep popup active
        return result if result else [path]

    def set_current_tag_prefix(self, prefix: str):
        """
        Set the current tag prefix for fuzzy matching.

        Called by parent dialog when user is typing in middle of comma-separated list.
        Only matches suggestions against this prefix.

        Args:
            prefix: Current tag being typed (trimmed whitespace)
        """
        self.current_prefix = prefix

    def update_tags(self, tags: List[str]):
        """
        Update the list of tags for fuzzy matching.

        Args:
            tags: New list of existing tags
        """
        self.tags = tags

        # Update the completer's model
        self.setModel(QStringListModel(tags))

    def pathFromIndex(self, index):
        """
        Override to return the completion text properly.

        Args:
            index: Model index of the selected item

        Returns:
            The completion text from the model
        """
        # Get the actual text from the model
        return self.model().data(index, Qt.ItemDataRole.DisplayRole)
