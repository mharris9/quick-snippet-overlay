"""
Configuration Manager - Application Settings Management

This module handles configuration loading, validation, persistence,
and default value management for the Quick Snippet Overlay application.

Key responsibilities:
- Load config.yaml with validation
- Provide default values for missing fields
- Validate configuration values (hotkeys, paths, ranges)
- Save configuration changes atomically
- Merge partial configs with defaults

Public API:
    ConfigManager(config_path: Optional[str] = None)
    - config: dict[str, Any] - Current configuration
    - get(key: str, default: Any = None) -> Any
    - set(key: str, value: Any) -> None
    - save() -> None
    - validate() -> tuple[bool, list[str]]

Author: Claude Code
Date: 2025-11-04
Phase: 4 - Configuration Management
"""

import yaml
import re
from pathlib import Path
from typing import Any, Optional
import tempfile
import shutil
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """
    Manages application configuration with validation and defaults.

    Handles loading, saving, and validating configuration values.
    Automatically creates default config if file is missing.
    Merges partial configs with defaults.
    """

    # Default configuration values (all 11 settings)
    DEFAULT_CONFIG = {
        "hotkey": "ctrl+shift+space",
        "snippet_file": str(Path.home() / "snippets" / "snippets.yaml"),
        "max_results": 10,
        "overlay_opacity": 0.95,
        "theme": "dark",
        "fuzzy_threshold": 60,
        "search_debounce_ms": 150,
        "auto_reload": True,
        "run_on_startup": False,
        "overlay_width": 600,
        "overlay_height": 400,
    }

    # Validation ranges for numeric settings
    VALIDATION_RANGES = {
        "max_results": (5, 20),
        "fuzzy_threshold": (40, 80),
        "search_debounce_ms": (50, 500),
        "overlay_opacity": (0.7, 1.0),
        "overlay_width": (400, 1200),
        "overlay_height": (300, 800),
    }

    # Valid theme options
    VALID_THEMES = {"dark", "light", "system"}

    # Hotkey validation pattern
    HOTKEY_PATTERN = re.compile(
        r"^(ctrl|shift|alt)(\+(ctrl|shift|alt))*\+([a-z0-9]+|space|enter|f\d{1,2})$",
        re.IGNORECASE,
    )

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize ConfigManager.

        Args:
            config_path: Path to config.yaml. If None, uses default location
                        (~/.config/quick-snippet-overlay/config.yaml on Linux/Mac,
                         ~/AppData/Local/quick-snippet-overlay/config.yaml on Windows)
        """
        if config_path is None:
            # Determine default config path based on platform
            if Path.home().joinpath("AppData").exists():  # Windows
                config_dir = Path.home() / "AppData" / "Local" / "quick-snippet-overlay"
            else:  # Linux/Mac
                config_dir = Path.home() / ".config" / "quick-snippet-overlay"

            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.yaml"
        else:
            self.config_path = Path(config_path)

        # Load configuration
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """
        Load configuration from file, creating default if missing.

        Returns:
            Configuration dictionary merged with defaults

        Handles:
            - Missing config file (creates default)
            - Malformed YAML (falls back to defaults)
            - Partial config (merges with defaults)
        """
        if not self.config_path.exists():
            logger.info(
                f"Config file not found at {self.config_path}, creating default"
            )
            return self._create_default_config()

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                loaded_config = yaml.safe_load(f) or {}

            # Merge with defaults (defaults provide missing values)
            merged_config = self._merge_with_defaults(loaded_config)

            logger.info(f"Loaded config from {self.config_path}")
            return merged_config

        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in config file: {e}, using defaults")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            logger.error(f"Error loading config: {e}, using defaults")
            return self.DEFAULT_CONFIG.copy()

    def _create_default_config(self) -> dict[str, Any]:
        """
        Create default config file and return default configuration.

        Returns:
            Default configuration dictionary
        """
        # Ensure parent directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Write default config to file
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                yaml.dump(
                    self.DEFAULT_CONFIG, f, default_flow_style=False, sort_keys=False
                )
            logger.info(f"Created default config at {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to create default config: {e}")

        return self.DEFAULT_CONFIG.copy()

    def _merge_with_defaults(self, loaded_config: dict[str, Any]) -> dict[str, Any]:
        """
        Merge loaded config with defaults, preserving unknown keys.

        Args:
            loaded_config: Configuration loaded from file

        Returns:
            Merged configuration with all required keys
        """
        # Start with defaults
        merged = self.DEFAULT_CONFIG.copy()

        # Update with loaded values (overrides defaults)
        merged.update(loaded_config)

        return merged

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.

        Args:
            key: Configuration key
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        return self.config.get(key, default)

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.

        Args:
            key: Configuration key
            value: New value

        Note: Does not automatically save to disk. Call save() to persist.
        """
        self.config[key] = value

    def save(self) -> None:
        """
        Save current configuration to disk atomically.

        Uses atomic write pattern (write to temp file, then rename)
        to prevent corruption if write fails.
        """
        try:
            # Ensure parent directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)

            # Write to temporary file first (atomic write pattern)
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.config_path.parent,
                delete=False,
                suffix=".yaml",
            ) as tmp_file:
                yaml.dump(
                    self.config, tmp_file, default_flow_style=False, sort_keys=False
                )
                tmp_path = Path(tmp_file.name)

            # Atomic rename (replaces existing file)
            shutil.move(str(tmp_path), str(self.config_path))

            logger.info(f"Saved config to {self.config_path}")

        except Exception as e:
            logger.error(f"Failed to save config: {e}")
            raise

    def validate(self) -> tuple[bool, list[str]]:
        """
        Validate current configuration.

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Validate hotkey format
        hotkey_valid, hotkey_errors = self._validate_hotkey(
            self.config.get("hotkey", "")
        )
        errors.extend(hotkey_errors)

        # Validate file path
        path_valid, path_errors = self._validate_file_path(
            self.config.get("snippet_file", "")
        )
        errors.extend(path_errors)

        # Validate numeric ranges
        for field, (min_val, max_val) in self.VALIDATION_RANGES.items():
            value = self.config.get(field)
            if value is not None:
                range_valid, range_errors = self._validate_range(
                    field, value, min_val, max_val
                )
                errors.extend(range_errors)

        # Validate theme
        theme = self.config.get("theme", "")
        if theme not in self.VALID_THEMES:
            errors.append(
                f"Invalid theme '{theme}', must be one of: {', '.join(self.VALID_THEMES)}"
            )

        return (len(errors) == 0, errors)

    def _validate_hotkey(self, hotkey: str) -> tuple[bool, list[str]]:
        """
        Validate hotkey format.

        Valid formats:
            - ctrl+shift+space
            - alt+f1
            - ctrl+alt+shift+k

        Invalid formats:
            - space (no modifier)
            - ctrl+ctrl+k (duplicate modifier)
            - invalid+k (unknown modifier)

        Args:
            hotkey: Hotkey string to validate

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        if not hotkey:
            errors.append("Hotkey cannot be empty")
            return (False, errors)

        # Check pattern match
        if not self.HOTKEY_PATTERN.match(hotkey):
            errors.append(f"Invalid hotkey format: '{hotkey}'")
            errors.append("Format: (ctrl|shift|alt)+...+key")
            return (False, errors)

        # Check for duplicate modifiers
        parts = hotkey.lower().split("+")
        modifiers = parts[:-1]  # All parts except the last (key)

        if len(modifiers) != len(set(modifiers)):
            errors.append(f"Duplicate modifiers in hotkey: '{hotkey}'")
            return (False, errors)

        return (True, [])

    def _validate_file_path(self, path: str) -> tuple[bool, list[str]]:
        """
        Validate snippet file path.

        Args:
            path: File path to validate

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        if not path or not path.strip():
            errors.append("Snippet file path cannot be empty")
            return (False, errors)

        # Just check it's a valid path format (doesn't need to exist yet)
        try:
            Path(path)
        except Exception as e:
            errors.append(f"Invalid file path format: {e}")
            return (False, errors)

        return (True, [])

    def _validate_range(
        self, field: str, value: Any, min_val: float, max_val: float
    ) -> tuple[bool, list[str]]:
        """
        Validate numeric value is within allowed range.

        Args:
            field: Field name
            value: Value to validate
            min_val: Minimum allowed value
            max_val: Maximum allowed value

        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []

        # Check type
        if not isinstance(value, (int, float)):
            errors.append(f"{field} must be numeric, got {type(value).__name__}")
            return (False, errors)

        # Check range
        if value < min_val or value > max_val:
            errors.append(f"{field} value {value} out of range [{min_val}, {max_val}]")
            return (False, errors)

        return (True, [])
