"""
Snippet Manager - Core Data Layer

This module handles snippet loading, validation, file watching,
backup management, and sample file creation.

Key responsibilities:
- Load snippets from YAML file with schema validation
- Create sample snippets.yaml if file missing (5+ example snippets)
- Watch file for changes with debounce (500ms to prevent reload thrashing)
- Backup management with rotation (up to 5 backups)
- Handle malformed YAML gracefully (load last good state)
- Auto-fix duplicate snippet IDs (append "-1", "-2", etc.)
"""

import yaml
import shutil
import logging
import time
from pathlib import Path
from dataclasses import dataclass
from datetime import date
from typing import List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# ============================================================================
# Logging Configuration
# ============================================================================

logging.basicConfig(
    filename="quick-snippet-overlay.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ============================================================================
# Snippet Data Class
# ============================================================================


@dataclass
class Snippet:
    """
    Represents a single text snippet with metadata.

    Attributes:
        id: Unique identifier for the snippet
        name: Display name for the snippet
        description: Search description
        content: The actual snippet text (may contain variables)
        tags: List of tags for categorization
        created: Creation date
        modified: Last modification date
    """

    id: str
    name: str
    description: str
    content: str
    tags: List[str]
    created: date
    modified: date

    def validate(self) -> bool:
        """
        Validate snippet has all required fields.

        Returns:
            True if snippet is valid, False otherwise
        """
        required = [self.id, self.name, self.content]
        return all(required) and len(self.id) > 0


# ============================================================================
# SnippetManager Class
# ============================================================================


class SnippetManager:
    """
    Manages snippet loading, validation, file watching, and backup creation.

    This class is responsible for:
    - Loading snippets from YAML file
    - Validating snippet schema
    - Watching for file changes with debounce
    - Creating backups with rotation (up to 5)
    - Auto-fixing duplicate snippet IDs
    - Creating sample file if missing

    Usage:
        manager = SnippetManager("C:/Users/mikeh/snippets/snippets.yaml")
        snippets = manager.load()
        manager.watch_file(callback=lambda: print("File changed"))
    """

    def __init__(self, file_path: str):
        """
        Initialize SnippetManager with file path.

        Args:
            file_path: Path to the snippets YAML file
        """
        self.file_path = Path(file_path)
        self.snippets: List[Snippet] = []
        self.last_good_state: List[Snippet] = []
        self._debounce_timer = None
        self._reload_pending = False

    def load(self) -> List[Snippet]:
        """
        Load snippets from YAML file.

        If file doesn't exist, creates a sample file.
        If file is malformed, falls back to last known good state.

        Returns:
            List of Snippet objects
        """
        if not self.file_path.exists():
            self._create_sample_file()

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data or "snippets" not in data:
                logger.warning(f"Invalid YAML structure in {self.file_path}")
                return self.last_good_state

            snippets = self._parse_snippets(data["snippets"])
            snippets = self._fix_duplicate_ids(snippets)
            self.snippets = snippets
            self.last_good_state = snippets
            logger.info(f"Loaded {len(snippets)} snippets from {self.file_path}")
            return snippets

        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {self.file_path}: {e}")
            return self.last_good_state

        except FileNotFoundError:
            self._create_sample_file()
            return self.load()

        except PermissionError as e:
            logger.warning(f"Permission denied reading {self.file_path}: {e}")
            return self.last_good_state

        except Exception as e:
            logger.error(f"Unexpected error loading snippets: {e}")
            return self.last_good_state

    def _create_sample_file(self):
        """
        Create sample snippets.yaml if missing.

        Creates a file with 5+ example snippets including:
        - PowerShell command
        - Python Flask launcher with variables
        - Git command
        - LLM prompt
        - Windows CLI command
        """
        sample_content = """version: 1
snippets:
  - id: ps-list-files
    name: List files by size
    description: PowerShell command to list files sorted by size
    content: |
      Get-ChildItem -Path . -File -Recurse |
      Sort-Object -Property Length -Descending |
      Select-Object -First 20 @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB,2)}}, FullName
    tags: [powershell, files, disk]
    created: 2025-11-04
    modified: 2025-11-04

  - id: flask-run
    name: Flask development server
    description: Start Flask app with custom port and debug enabled
    content: |
      python -m flask --app {{app_name:app}} run --debug --port {{port:5000}}
    tags: [python, flask, development]
    created: 2025-11-04
    modified: 2025-11-04

  - id: git-uncommit
    name: Undo last commit (keep changes)
    description: Git command to undo last commit but keep changes in working directory
    content: git reset --soft HEAD~1
    tags: [git, version-control]
    created: 2025-11-04
    modified: 2025-11-04

  - id: llm-code-review
    name: Code review prompt
    description: Request detailed code review from LLM
    content: |
      Please review the following code for:
      - Performance issues
      - Security vulnerabilities
      - Code style and readability
      - Edge cases and error handling

      Code:
      ```
      {{code_snippet}}
      ```
    tags: [llm, code-review, ai]
    created: 2025-11-04
    modified: 2025-11-04

  - id: win-reset-network
    name: Reset network adapter
    description: Reset all network settings (requires admin)
    content: |
      ipconfig /release
      ipconfig /renew
      netsh winsock reset catalog
      netsh int ip reset reset.log
    tags: [windows, network, admin]
    created: 2025-11-04
    modified: 2025-11-04

  - id: ps-file-search
    name: Find file by pattern
    description: Search for files matching name pattern, return metadata
    content: |
      Get-ChildItem -Path {{search_path:.}} -Filter {{pattern:*.txt}} -Recurse -ErrorAction SilentlyContinue |
      Select-Object FullName, @{Name="Size(KB)";Expression={[math]::Round($_.Length/1KB,2)}}, LastWriteTime |
      Sort-Object LastWriteTime -Descending
    tags: [powershell, files, search]
    created: 2025-11-04
    modified: 2025-11-04
"""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(sample_content, encoding="utf-8")
        logger.info(f"Created sample snippets file at {self.file_path}")

    def _parse_snippets(self, data: List[dict]) -> List[Snippet]:
        """
        Parse snippet dictionaries into Snippet objects.

        Args:
            data: List of snippet dictionaries from YAML

        Returns:
            List of valid Snippet objects
        """
        snippets = []
        for snippet_dict in data:
            try:
                # Validate required fields
                if not self._validate_schema(snippet_dict):
                    logger.warning(
                        f"Invalid snippet schema: {snippet_dict.get('id', 'unknown')}"
                    )
                    continue

                # Parse dates
                created = snippet_dict.get("created")
                modified = snippet_dict.get("modified")

                if isinstance(created, str):
                    created = date.fromisoformat(created)
                elif not isinstance(created, date):
                    created = date.today()

                if isinstance(modified, str):
                    modified = date.fromisoformat(modified)
                elif not isinstance(modified, date):
                    modified = date.today()

                # Create Snippet object
                snippet = Snippet(
                    id=snippet_dict["id"],
                    name=snippet_dict["name"],
                    description=snippet_dict.get("description", ""),
                    content=snippet_dict["content"],
                    tags=snippet_dict.get("tags", []),
                    created=created,
                    modified=modified,
                )

                # Validate snippet
                if snippet.validate():
                    snippets.append(snippet)
                else:
                    logger.warning(f"Snippet validation failed: {snippet.id}")

            except Exception as e:
                logger.warning(f"Error parsing snippet: {e}")
                continue

        return snippets

    def _validate_schema(self, snippet_dict: dict) -> bool:
        """
        Validate snippet dictionary has required fields.

        Args:
            snippet_dict: Dictionary containing snippet data

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["id", "name", "content"]

        for field in required_fields:
            if field not in snippet_dict or not snippet_dict[field]:
                return False

        return True

    def _fix_duplicate_ids(self, snippets: List[Snippet]) -> List[Snippet]:
        """
        Fix duplicate snippet IDs by appending -1, -2, etc.

        Args:
            snippets: List of snippets (may contain duplicates)

        Returns:
            List of snippets with unique IDs
        """
        seen_ids = {}

        for snippet in snippets:
            if snippet.id in seen_ids:
                counter = 1
                new_id = f"{snippet.id}-{counter}"
                while new_id in seen_ids:
                    counter += 1
                    new_id = f"{snippet.id}-{counter}"

                logger.warning(f"Duplicate ID '{snippet.id}' renamed to '{new_id}'")
                snippet.id = new_id

            seen_ids[snippet.id] = True

        return snippets

    def create_backup(self):
        """
        Create backup file before write operations.

        Rotates backups: .005 → delete, .004 → .005, ..., current → .001
        Maintains maximum of 5 backups.
        """
        try:
            # Rotate backups: shift old backups
            for i in range(5, 0, -1):
                backup_file = Path(f"{self.file_path}.backup.{i:03d}")
                if i == 5 and backup_file.exists():
                    backup_file.unlink()  # Delete oldest
                elif i < 5:
                    next_backup = Path(f"{self.file_path}.backup.{i+1:03d}")
                    if backup_file.exists():
                        backup_file.rename(next_backup)

            # Create new backup.001 from current file
            if self.file_path.exists():
                backup_path = Path(f"{self.file_path}.backup.001")
                shutil.copy2(self.file_path, backup_path)
                logger.info(f"Created backup: {backup_path}")

        except Exception as e:
            logger.warning(f"Could not create backup: {e}")

    def watch_file(self, callback):
        """
        Start file watcher for auto-reload with debounce.

        Args:
            callback: Function to call when file changes

        Returns:
            Observer object (must be stopped when done)
        """

        class DebouncedHandler(FileSystemEventHandler):
            """File system event handler with debounce logic."""

            def __init__(self, manager, callback):
                self.manager = manager
                self.callback = callback
                self.last_reload = 0
                self.debounce_delay = 0.5  # 500ms

            def on_modified(self, event):
                """Handle file modification event."""
                if event.src_path.endswith("snippets.yaml"):
                    now = time.time()
                    if now - self.last_reload > self.debounce_delay:
                        self.last_reload = now
                        self.callback()

        handler = DebouncedHandler(self, callback)
        observer = Observer()
        observer.schedule(handler, path=str(self.file_path.parent), recursive=False)
        observer.start()
        logger.info(f"Started file watcher for {self.file_path}")
        return observer

    def add_snippet(self, snippet_data: dict) -> bool:
        """
        Append a new snippet to the YAML file.

        Args:
            snippet_data: Dictionary with snippet fields (id, name, description, content, tags, created, modified)

        Returns:
            True if successful, False otherwise
        """
        try:
            # Load current YAML data
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)

            if not data:
                data = {"snippets": []}

            # Check for duplicate ID
            existing_ids = {s["id"] for s in data.get("snippets", [])}
            original_id = snippet_data["id"]
            snippet_id = original_id
            counter = 1

            while snippet_id in existing_ids:
                snippet_id = f"{original_id}-{counter}"
                counter += 1

            # Update ID if changed
            snippet_data["id"] = snippet_id

            # Append new snippet
            data.setdefault("snippets", []).append(snippet_data)

            # Write back to file
            with open(self.file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            logger.info(f"Added new snippet: {snippet_data['name']} (ID: {snippet_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to add snippet: {e}")
            return False

    def get_all_tags(self) -> List[str]:
        """
        Get all unique tags from loaded snippets.

        Returns:
            Sorted list of unique tags from all snippets
        """
        tags = set()
        for snippet in self.snippets:
            tags.update(snippet.tags)
        return sorted(tags)

    def delete_snippets(self, snippet_ids: List[str]) -> None:
        """
        Delete multiple snippets by their IDs.

        Args:
            snippet_ids: List of snippet IDs to delete

        Raises:
            ValueError: If any snippet ID is not found
            IOError: If YAML file cannot be written
        """
        # Load current snippets
        current_snippets = self.load()

        # Verify all IDs exist
        existing_ids = {s.id for s in current_snippets}
        for snippet_id in snippet_ids:
            if snippet_id not in existing_ids:
                raise ValueError(f"Snippet with ID '{snippet_id}' not found")

        # Filter out snippets to delete
        remaining_snippets = [s for s in current_snippets if s.id not in snippet_ids]

        # Save updated snippets
        self._save_snippets(remaining_snippets)

        logger.info(f"Deleted {len(snippet_ids)} snippet(s): {snippet_ids}")

    def _save_snippets(self, snippets: List[Snippet]) -> None:
        """
        Save snippets to YAML file.

        Args:
            snippets: List of Snippet objects to save

        Raises:
            IOError: If file cannot be written
        """
        # Convert snippets to dict format
        snippets_data = {
            "version": 1,
            "snippets": [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "content": s.content,
                    "tags": s.tags,
                    "created": s.created.isoformat()
                    if isinstance(s.created, date)
                    else s.created,
                    "modified": s.modified.isoformat()
                    if isinstance(s.modified, date)
                    else s.modified,
                }
                for s in snippets
            ],
        }

        # Write to file
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    snippets_data,
                    f,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

            logger.info(f"Saved {len(snippets)} snippets to {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to save snippets: {e}")
            raise IOError(f"Failed to save snippets: {e}")

    def get_all_snippets(self) -> List[Snippet]:
        """
        Get all snippets (convenience method).

        Returns:
            List of all Snippet objects
        """
        return self.load()
