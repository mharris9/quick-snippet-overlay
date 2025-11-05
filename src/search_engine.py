"""
Search engine with fuzzy matching and weighted scoring.

This module provides fuzzy search functionality across snippet fields using
rapidfuzz for typo-tolerant matching with Levenshtein distance.

Features:
- Fuzzy search across name, description, tags, and content fields
- Weighted scoring (name: 3x, description: 2x, tags: 2x, content: 1x)
- Typo tolerance using rapidfuzz
- Threshold filtering
- Results sorted by relevance score
"""

from typing import List, Dict, Any
from rapidfuzz import fuzz
from src.snippet_manager import Snippet


# Field weight constants
WEIGHT_NAME = 3.0
WEIGHT_DESCRIPTION = 2.0
WEIGHT_TAGS = 2.0
WEIGHT_CONTENT = 1.0


class SearchEngine:
    """
    Fuzzy search engine for snippets with weighted multi-field scoring.

    The SearchEngine uses rapidfuzz for typo-tolerant fuzzy matching across
    multiple snippet fields. Each field is weighted differently to prioritize
    matches in more important fields (e.g., name over content).

    Field Weights:
        - name: 3x
        - description: 2x
        - tags: 2x
        - content: 1x

    Example:
        >>> manager = SnippetManager("snippets.yaml")
        >>> snippets = manager.load()
        >>> engine = SearchEngine(snippets)
        >>> results = engine.search("flask", threshold=60)
        >>> for result in results[:5]:
        ...     print(f"{result['snippet'].name}: {result['score']:.1f}")
    """

    def __init__(self, snippets: List[Snippet]):
        """
        Initialize search engine with a list of snippets.

        Args:
            snippets: List of Snippet objects to search
        """
        self.snippets = snippets

    def search(self, query: str, threshold: int = 60) -> List[Dict[str, Any]]:
        """
        Search snippets using fuzzy matching with weighted scoring.

        Searches across all snippet fields (name, description, tags, content)
        and returns results ranked by relevance score. Uses fuzzy matching
        to handle typos and partial matches.

        Args:
            query: Search query string
            threshold: Minimum score (0-100) for results to be included.
                      Default is 60.

        Returns:
            List of dicts containing 'snippet' and 'score' keys, sorted by
            score in descending order. Empty list if no matches found.

        Example:
            >>> results = engine.search("flsk", threshold=50)  # Typo for "flask"
            >>> len(results) > 0  # Should still find flask snippets
            True
            >>> results[0]['score'] >= results[1]['score']  # Sorted by score
            True
        """
        # Handle empty or whitespace-only queries
        if not query or not query.strip():
            return []

        query = query.strip().lower()
        results = []

        for snippet in self.snippets:
            # Calculate weighted score for this snippet
            score = self._calculate_snippet_score(snippet, query)

            # Only include results above threshold
            if score >= threshold:
                results.append({
                    "snippet": snippet,
                    "score": score
                })

        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)

        return results

    def _calculate_snippet_score(self, snippet: Snippet, query: str) -> float:
        """
        Calculate weighted relevance score for a snippet against a query.

        Uses partial_ratio from rapidfuzz to allow substring matches and
        typo tolerance. Each field is scored separately and combined using
        field-specific weights.

        Args:
            snippet: Snippet object to score
            query: Normalized query string (lowercase, trimmed)

        Returns:
            Combined weighted score (0-100 scale)
        """
        scores = []

        # Score name field (weight: 3x)
        if snippet.name:
            name_score = fuzz.partial_ratio(
                query,
                snippet.name.lower(),
                score_cutoff=0
            )
            scores.append(name_score * WEIGHT_NAME)

        # Score description field (weight: 2x)
        if snippet.description:
            desc_score = fuzz.partial_ratio(
                query,
                snippet.description.lower(),
                score_cutoff=0
            )
            scores.append(desc_score * WEIGHT_DESCRIPTION)

        # Score tags field (weight: 2x)
        # Take the maximum score across all tags
        if snippet.tags:
            tag_scores = [
                fuzz.partial_ratio(query, tag.lower(), score_cutoff=0)
                for tag in snippet.tags
            ]
            if tag_scores:
                max_tag_score = max(tag_scores)
                scores.append(max_tag_score * WEIGHT_TAGS)

        # Score content field (weight: 1x)
        if snippet.content:
            content_score = fuzz.partial_ratio(
                query,
                snippet.content.lower(),
                score_cutoff=0
            )
            scores.append(content_score * WEIGHT_CONTENT)

        # Calculate weighted average
        if not scores:
            return 0.0

        # Sum of weights used
        total_weight = 0.0
        if snippet.name:
            total_weight += WEIGHT_NAME
        if snippet.description:
            total_weight += WEIGHT_DESCRIPTION
        if snippet.tags:
            total_weight += WEIGHT_TAGS
        if snippet.content:
            total_weight += WEIGHT_CONTENT

        # Weighted average (normalize to 0-100 scale)
        weighted_score = sum(scores) / total_weight if total_weight > 0 else 0.0

        return round(weighted_score, 2)
