"""
Tests for main.py - Application entry point and single instance enforcement

This module tests:
- Single instance enforcement via lock file
- Lock file creation and cleanup
- Stale lock file handling
- Application startup sequence
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock


@pytest.fixture
def temp_lock_file(monkeypatch):
    """Create temporary lock file path for testing."""
    temp_dir = tempfile.mkdtemp()
    lock_file = os.path.join(temp_dir, 'app.lock')
    monkeypatch.setattr('src.main.LOCK_FILE', lock_file)
    yield lock_file
    # Cleanup
    if os.path.exists(lock_file):
        try:
            os.remove(lock_file)
        except:
            pass
    try:
        os.rmdir(temp_dir)
    except:
        pass


def test_lock_file_creation(temp_lock_file):
    """Test that lock file is created with current PID."""
    from src.main import ensure_single_instance
    import os

    # Ensure lock file doesn't exist
    assert not os.path.exists(temp_lock_file)

    # Create lock file
    ensure_single_instance()

    # Verify lock file exists
    assert os.path.exists(temp_lock_file)

    # Verify lock file contains current PID
    with open(temp_lock_file, 'r') as f:
        pid = int(f.read().strip())
    assert pid == os.getpid()


def test_single_instance_enforcement(temp_lock_file):
    """Test that second instance is prevented when first is running."""
    from src.main import ensure_single_instance
    import os

    # Create first instance lock file
    ensure_single_instance()
    assert os.path.exists(temp_lock_file)

    # Try to create second instance (should raise SystemExit)
    with patch('src.main.QMessageBox.critical'):
        with pytest.raises(SystemExit) as excinfo:
            ensure_single_instance()

        # Verify exit code is 1
        assert excinfo.value.code == 1


@patch('src.main.is_process_running')
def test_stale_lock_file_handling(mock_is_running, temp_lock_file):
    """Test that stale lock file (dead PID) is removed and app continues."""
    from src.main import ensure_single_instance
    import os

    # Create stale lock file with dead PID
    dead_pid = 99999
    os.makedirs(os.path.dirname(temp_lock_file), exist_ok=True)
    with open(temp_lock_file, 'w') as f:
        f.write(str(dead_pid))

    # Mock process check to return False (dead process)
    mock_is_running.return_value = False

    # Should remove stale lock and create new one
    ensure_single_instance()

    # Verify new lock file has current PID
    with open(temp_lock_file, 'r') as f:
        pid = int(f.read().strip())
    assert pid == os.getpid()

    # Verify process check was called with dead PID
    mock_is_running.assert_called_with(dead_pid)


def test_lock_file_cleanup(temp_lock_file):
    """Test that cleanup_lock_file removes lock file."""
    from src.main import cleanup_lock_file
    import os

    # Create lock file
    os.makedirs(os.path.dirname(temp_lock_file), exist_ok=True)
    with open(temp_lock_file, 'w') as f:
        f.write(str(os.getpid()))

    assert os.path.exists(temp_lock_file)

    # Cleanup
    cleanup_lock_file()

    # Verify lock file removed
    assert not os.path.exists(temp_lock_file)


def test_cleanup_lock_file_when_not_exists(temp_lock_file):
    """Test that cleanup_lock_file handles missing lock file gracefully."""
    from src.main import cleanup_lock_file

    # Ensure lock file doesn't exist
    assert not os.path.exists(temp_lock_file)

    # Should not raise error
    cleanup_lock_file()


@patch('sys.platform', 'win32')
def test_is_process_running_windows():
    """Test process running check on Windows."""
    from src.main import is_process_running
    import os

    # Test with current process (should be running)
    assert is_process_running(os.getpid()) is True

    # Test with invalid PID (should not be running)
    assert is_process_running(99999) is False


def test_application_startup_components():
    """Test that application components are initialized in correct order."""
    from src.main import main

    with patch('src.main.ensure_single_instance'):
        with patch('src.main.atexit.register'):
            with patch('src.main.QApplication') as mock_qapp_class:
                with patch('src.main.ConfigManager') as mock_config:
                    with patch('src.main.SnippetManager') as mock_snippet:
                        with patch('src.main.SearchEngine') as mock_search:
                            with patch('src.main.OverlayWindow') as mock_overlay:
                                with patch('src.main.SystemTray') as mock_tray:
                                    with patch('src.main.HotkeyManager') as mock_hotkey:
                                        # Mock QApplication instance
                                        mock_app = Mock()
                                        mock_app.exec.return_value = 0
                                        mock_qapp_class.return_value = mock_app

                                        # Mock config manager
                                        mock_config_instance = Mock()
                                        mock_config_instance.get.return_value = 'ctrl+shift+space'
                                        mock_config.return_value = mock_config_instance

                                        # Mock hotkey manager
                                        mock_hotkey_instance = Mock()
                                        mock_hotkey.return_value = mock_hotkey_instance

                                        # Run main
                                        with pytest.raises(SystemExit) as excinfo:
                                            main()

                                        # Verify components were created
                                        mock_config.assert_called_once()
                                        mock_snippet.assert_called_once()
                                        mock_search.assert_called_once()

                                        # Verify hotkey listener was started
                                        mock_hotkey_instance.start.assert_called_once()


def test_lock_file_directory_created():
    """Test that lock file directory is created if it doesn't exist."""
    from src.main import ensure_single_instance
    import os

    with tempfile.TemporaryDirectory() as temp_dir:
        lock_file = os.path.join(temp_dir, 'subdir', 'app.lock')

        with patch('src.main.LOCK_FILE', lock_file):
            # Verify subdir doesn't exist
            assert not os.path.exists(os.path.dirname(lock_file))

            # Create lock file (should create directory)
            ensure_single_instance()

            # Verify directory was created
            assert os.path.exists(os.path.dirname(lock_file))
            assert os.path.exists(lock_file)
