"""
Tests for Configuration Manager

Test-Driven Development: These tests define the ConfigManager API
before implementation. All tests should fail initially.

Phase 4: Configuration Management
Target: 8-10 tests, ≥95% coverage
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import os


class TestConfigLoading:
    """Test configuration loading from files"""

    def test_load_valid_config(self):
        """Load configuration from valid YAML file"""
        from src.config_manager import ConfigManager

        # Create temporary valid config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            yaml.dump({
                'hotkey': 'ctrl+alt+s',
                'snippet_file': 'C:\\Users\\test\\snippets.yaml',
                'max_results': 15,
                'overlay_opacity': 0.85,
                'theme': 'light',
                'fuzzy_threshold': 70,
                'search_debounce_ms': 200,
                'auto_reload': False,
                'run_on_startup': True,
                'overlay_width': 800,
                'overlay_height': 500
            }, f)

        try:
            # Load config
            manager = ConfigManager(config_path)
            config = manager.config

            # Verify all 11 values loaded correctly
            assert config['hotkey'] == 'ctrl+alt+s'
            assert config['snippet_file'] == 'C:\\Users\\test\\snippets.yaml'
            assert config['max_results'] == 15
            assert config['overlay_opacity'] == 0.85
            assert config['theme'] == 'light'
            assert config['fuzzy_threshold'] == 70
            assert config['search_debounce_ms'] == 200
            assert config['auto_reload'] is False
            assert config['run_on_startup'] is True
            assert config['overlay_width'] == 800
            assert config['overlay_height'] == 500
        finally:
            os.unlink(config_path)

    def test_load_missing_config_creates_default(self):
        """When config file missing, create default config.yaml"""
        from src.config_manager import ConfigManager

        # Create path to non-existent config file
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'

            # Config file should not exist yet
            assert not config_path.exists()

            # Load should create default config
            manager = ConfigManager(str(config_path))

            # File should now exist
            assert config_path.exists()

            # Verify all 11 defaults
            config = manager.config
            assert config['hotkey'] == 'ctrl+shift+space'
            assert 'snippets.yaml' in config['snippet_file']  # Default path includes snippets.yaml
            assert config['max_results'] == 10
            assert config['overlay_opacity'] == 0.95
            assert config['theme'] == 'dark'
            assert config['fuzzy_threshold'] == 60
            assert config['search_debounce_ms'] == 150
            assert config['auto_reload'] is True
            assert config['run_on_startup'] is False
            assert config['overlay_width'] == 600
            assert config['overlay_height'] == 400

    def test_load_invalid_yaml_config(self):
        """When config YAML is malformed, fall back to defaults"""
        from src.config_manager import ConfigManager

        # Create malformed YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write("invalid: yaml: content:\n  - broken\n  missing_quote: \"unclosed")

        try:
            # Load should fall back to defaults
            manager = ConfigManager(config_path)
            config = manager.config

            # Verify defaults are used
            assert config['hotkey'] == 'ctrl+shift+space'
            assert config['max_results'] == 10
            assert config['theme'] == 'dark'
        finally:
            os.unlink(config_path)

    def test_missing_fields_use_defaults(self):
        """Partial config files should merge with defaults"""
        from src.config_manager import ConfigManager

        # Create partial config with only 3 fields
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            yaml.dump({
                'hotkey': 'alt+space',
                'max_results': 20,
                'theme': 'light'
            }, f)

        try:
            # Load should merge with defaults
            manager = ConfigManager(config_path)
            config = manager.config

            # Verify custom values
            assert config['hotkey'] == 'alt+space'
            assert config['max_results'] == 20
            assert config['theme'] == 'light'

            # Verify other 8 fields use defaults
            assert 'snippets.yaml' in config['snippet_file']
            assert config['overlay_opacity'] == 0.95
            assert config['fuzzy_threshold'] == 60
            assert config['search_debounce_ms'] == 150
            assert config['auto_reload'] is True
            assert config['run_on_startup'] is False
            assert config['overlay_width'] == 600
            assert config['overlay_height'] == 400
        finally:
            os.unlink(config_path)


class TestConfigValidation:
    """Test configuration value validation"""

    def test_validate_hotkey_format(self):
        """Validate hotkey format (ctrl|shift|alt)+...+key"""
        from src.config_manager import ConfigManager

        # Test valid hotkey patterns
        valid_hotkeys = [
            'ctrl+shift+space',
            'alt+f1',
            'ctrl+alt+shift+k',
            'shift+enter',
            'ctrl+f12',
            'alt+shift+a'
        ]

        for hotkey in valid_hotkeys:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'hotkey': hotkey}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert is_valid, f"Hotkey '{hotkey}' should be valid, errors: {errors}"
            finally:
                os.unlink(config_path)

        # Test invalid hotkey patterns
        invalid_hotkeys = [
            ('space', 'no modifier'),
            ('k', 'no modifier'),
            ('ctrl+ctrl+k', 'duplicate modifier'),
            ('shift+shift+a', 'duplicate modifier'),
            ('invalid+k', 'unknown modifier'),
            ('', 'empty hotkey')
        ]

        for hotkey, reason in invalid_hotkeys:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'hotkey': hotkey}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert not is_valid, f"Hotkey '{hotkey}' should be invalid ({reason})"
                assert len(errors) > 0
            finally:
                os.unlink(config_path)

    def test_validate_file_path(self):
        """Validate snippet file path is non-empty"""
        from src.config_manager import ConfigManager

        # Valid paths
        valid_paths = [
            'C:\\Users\\test\\snippets.yaml',
            '/home/user/snippets.yaml',
            'snippets.yaml',
            '../config/snippets.yaml'
        ]

        for path in valid_paths:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'snippet_file': path}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert is_valid, f"Path '{path}' should be valid, errors: {errors}"
            finally:
                os.unlink(config_path)

        # Invalid paths
        invalid_paths = ['', '   ', None]

        for path in invalid_paths:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'snippet_file': path}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert not is_valid, f"Path '{path}' should be invalid"
                assert len(errors) > 0
            finally:
                os.unlink(config_path)

    def test_validate_numeric_ranges(self):
        """Validate numeric settings are within allowed ranges"""
        from src.config_manager import ConfigManager

        # Test each numeric setting
        test_cases = [
            # (field, valid_value, invalid_low, invalid_high)
            ('max_results', 10, 3, 25),
            ('fuzzy_threshold', 60, 30, 90),
            ('search_debounce_ms', 150, 20, 600),
            ('overlay_opacity', 0.9, 0.5, 1.1),
            ('overlay_width', 600, 300, 1500),
            ('overlay_height', 400, 200, 900)
        ]

        for field, valid_val, invalid_low, invalid_high in test_cases:
            # Test valid value
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({field: valid_val}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert is_valid, f"{field}={valid_val} should be valid, errors: {errors}"
            finally:
                os.unlink(config_path)

            # Test invalid low value
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({field: invalid_low}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert not is_valid, f"{field}={invalid_low} should be invalid (too low)"
                assert any(field in err for err in errors)
            finally:
                os.unlink(config_path)

            # Test invalid high value
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({field: invalid_high}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert not is_valid, f"{field}={invalid_high} should be invalid (too high)"
                assert any(field in err for err in errors)
            finally:
                os.unlink(config_path)

    def test_validate_theme_options(self):
        """Validate theme is one of: dark, light, system"""
        from src.config_manager import ConfigManager

        # Valid themes
        valid_themes = ['dark', 'light', 'system']

        for theme in valid_themes:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'theme': theme}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert is_valid, f"Theme '{theme}' should be valid, errors: {errors}"
            finally:
                os.unlink(config_path)

        # Invalid themes
        invalid_themes = ['blue', 'custom', 'auto', '']

        for theme in invalid_themes:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
                config_path = f.name
                yaml.dump({'theme': theme}, f)

            try:
                manager = ConfigManager(config_path)
                is_valid, errors = manager.validate()
                assert not is_valid, f"Theme '{theme}' should be invalid"
                assert any('theme' in err.lower() for err in errors)
            finally:
                os.unlink(config_path)


class TestConfigPersistence:
    """Test configuration saving and reloading"""

    def test_save_config(self):
        """Save modified configuration to disk"""
        from src.config_manager import ConfigManager

        # Create initial config
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'

            # Create manager with defaults
            manager = ConfigManager(str(config_path))

            # Modify configuration
            manager.set('hotkey', 'alt+ctrl+f')
            manager.set('max_results', 15)
            manager.set('theme', 'light')

            # Save to disk
            manager.save()

            # Create new manager instance to reload
            manager2 = ConfigManager(str(config_path))

            # Verify changes persisted
            assert manager2.get('hotkey') == 'alt+ctrl+f'
            assert manager2.get('max_results') == 15
            assert manager2.get('theme') == 'light'

            # Verify other values still default
            assert manager2.get('fuzzy_threshold') == 60
            assert manager2.get('auto_reload') is True

    def test_get_set_config_values(self):
        """Get and set individual config values"""
        from src.config_manager import ConfigManager

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            manager = ConfigManager(str(config_path))

            # Test get with existing key
            assert manager.get('hotkey') == 'ctrl+shift+space'
            assert manager.get('max_results') == 10

            # Test get with non-existing key and default
            assert manager.get('nonexistent', 'default_value') == 'default_value'
            assert manager.get('missing') is None

            # Test set
            manager.set('hotkey', 'shift+f1')
            assert manager.get('hotkey') == 'shift+f1'

            manager.set('max_results', 20)
            assert manager.get('max_results') == 20

            # Set new custom key
            manager.set('custom_key', 'custom_value')
            assert manager.get('custom_key') == 'custom_value'


class TestConfigEdgeCases:
    """Test edge cases and error handling"""

    def test_config_with_unknown_keys(self):
        """Unknown keys in config file should be preserved"""
        from src.config_manager import ConfigManager

        # Create config with known and unknown keys
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            yaml.dump({
                'hotkey': 'ctrl+space',
                'custom_field': 'custom_value',
                'another_unknown': 42,
                'max_results': 15
            }, f)

        try:
            # Load config
            manager = ConfigManager(config_path)

            # Verify known keys work
            assert manager.get('hotkey') == 'ctrl+space'
            assert manager.get('max_results') == 15

            # Verify unknown keys are preserved
            assert manager.get('custom_field') == 'custom_value'
            assert manager.get('another_unknown') == 42

            # Save and reload to verify persistence
            manager.save()
            manager2 = ConfigManager(config_path)

            # Unknown keys should still be there
            assert manager2.get('custom_field') == 'custom_value'
            assert manager2.get('another_unknown') == 42
        finally:
            os.unlink(config_path)

    def test_empty_config_file(self):
        """Empty config file should use all defaults"""
        from src.config_manager import ConfigManager

        # Create empty YAML file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            f.write('')  # Empty file

        try:
            # Load should use all defaults
            manager = ConfigManager(config_path)

            # Verify all 11 defaults are present
            assert manager.get('hotkey') == 'ctrl+shift+space'
            assert 'snippets.yaml' in manager.get('snippet_file')
            assert manager.get('max_results') == 10
            assert manager.get('overlay_opacity') == 0.95
            assert manager.get('theme') == 'dark'
            assert manager.get('fuzzy_threshold') == 60
            assert manager.get('search_debounce_ms') == 150
            assert manager.get('auto_reload') is True
            assert manager.get('run_on_startup') is False
            assert manager.get('overlay_width') == 600
            assert manager.get('overlay_height') == 400
        finally:
            os.unlink(config_path)

    def test_default_config_path_auto_creation(self):
        """Test ConfigManager with no path argument creates default location"""
        from src.config_manager import ConfigManager
        from unittest.mock import patch

        # Test Windows path (AppData exists)
        manager = ConfigManager()
        assert manager.config_path is not None
        assert manager.config_path.exists()
        assert manager.get('hotkey') == 'ctrl+shift+space'

        # Cleanup Windows config
        if manager.config_path.exists():
            os.unlink(manager.config_path)

        # Test Linux/Mac path (AppData doesn't exist)
        # Mock Path.home().joinpath('AppData').exists() to return False
        with patch.object(Path, 'exists', return_value=False):
            with tempfile.TemporaryDirectory() as tmpdir:
                # Mock Path.home() to return tmpdir
                with patch('pathlib.Path.home', return_value=Path(tmpdir)):
                    manager2 = ConfigManager()
                    # Should create .config/quick-snippet-overlay path
                    assert '.config' in str(manager2.config_path) or 'quick-snippet-overlay' in str(manager2.config_path)

    def test_save_config_error_handling(self):
        """Test save() handles errors gracefully"""
        from src.config_manager import ConfigManager
        from unittest.mock import patch, MagicMock

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'
            manager = ConfigManager(str(config_path))

            # Mock tempfile.NamedTemporaryFile to raise exception
            with patch('tempfile.NamedTemporaryFile') as mock_temp:
                mock_temp.side_effect = PermissionError("Cannot write to directory")

                # save() should raise the exception
                try:
                    manager.save()
                    assert False, "Expected exception to be raised"
                except PermissionError:
                    pass  # Expected

    def test_validate_type_errors(self):
        """Test validation catches type errors in numeric fields"""
        from src.config_manager import ConfigManager

        # Create config with wrong types
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
            yaml.dump({
                'max_results': 'ten',  # Should be int
                'overlay_opacity': 'high'  # Should be float
            }, f)

        try:
            manager = ConfigManager(config_path)
            is_valid, errors = manager.validate()

            # Should detect type errors
            assert not is_valid
            assert len(errors) >= 2  # At least 2 type errors
        finally:
            os.unlink(config_path)

    def test_create_default_config_with_write_error(self):
        """Test that create_default_config handles write errors gracefully"""
        from src.config_manager import ConfigManager
        from unittest.mock import patch

        # Create a non-existent path
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'subdir' / 'config.yaml'

            # Mock open() to raise exception when trying to write default config
            with patch('builtins.open', side_effect=PermissionError("Cannot write")):
                # Should still initialize with default values even if write fails
                manager = ConfigManager(str(config_path))

                # Config should be defaults even though file creation failed
                assert manager.config['hotkey'] == 'ctrl+shift+space'
                assert manager.config['max_results'] == 10

    def test_load_config_general_exception(self):
        """Test load_config handles general exceptions during file read"""
        from src.config_manager import ConfigManager
        from unittest.mock import patch, mock_open

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / 'config.yaml'

            # Create a valid file first
            with open(config_path, 'w') as f:
                yaml.dump({'hotkey': 'ctrl+space'}, f)

            # Mock open() to raise unexpected exception
            with patch('builtins.open', side_effect=OSError("Unexpected read error")):
                # Should fall back to defaults
                manager = ConfigManager(str(config_path))
                assert manager.config['hotkey'] == 'ctrl+shift+space'  # Default, not 'ctrl+space'


# Test fixtures will be created in tests/fixtures/config/
