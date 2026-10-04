from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from virtualbox_rpc.startup import (
    APP_NAME,
    get_startup_command,
    is_startup_registered,
    register_startup,
    unregister_startup,
)


def test_get_startup_command():
    cmd = get_startup_command()
    assert isinstance(cmd, str)
    assert len(cmd) > 0


def test_non_windows_platform(monkeypatch):
    monkeypatch.setattr("virtualbox_rpc.startup.is_windows", lambda: False)
    assert is_startup_registered() is False
    assert register_startup() is False
    assert unregister_startup() is False


def test_startup_registration_mocked(monkeypatch):
    monkeypatch.setattr("virtualbox_rpc.startup.is_windows", lambda: True)

    mock_winreg = MagicMock()
    mock_key = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
    mock_winreg.HKEY_CURRENT_USER = "HKEY_CURRENT_USER"
    mock_winreg.KEY_READ = 1
    mock_winreg.KEY_SET_VALUE = 2
    mock_winreg.REG_SZ = 1

    with patch.dict(sys.modules, {"winreg": mock_winreg}):
        # Test registration
        success = register_startup('test_cmd')
        assert success is True
        mock_winreg.SetValueEx.assert_called_with(
            mock_key, APP_NAME, 0, mock_winreg.REG_SZ, 'test_cmd'
        )

        # Test query
        mock_winreg.QueryValueEx.return_value = ('test_cmd', 1)
        assert is_startup_registered() is True

        # Test unregistration
        success = unregister_startup()
        assert success is True
        mock_winreg.DeleteValue.assert_called_with(mock_key, APP_NAME)


def test_unregister_not_found(monkeypatch):
    monkeypatch.setattr("virtualbox_rpc.startup.is_windows", lambda: True)

    mock_winreg = MagicMock()
    mock_key = MagicMock()
    mock_winreg.OpenKey.return_value.__enter__.return_value = mock_key
    mock_winreg.DeleteValue.side_effect = FileNotFoundError()

    with patch.dict(sys.modules, {"winreg": mock_winreg}):
        assert unregister_startup() is True
