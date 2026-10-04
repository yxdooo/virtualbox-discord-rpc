from __future__ import annotations

import sys
from unittest.mock import patch

import pytest

from virtualbox_rpc.__main__ import main, setup_logging


def test_setup_logging(tmp_path):
    log_file = tmp_path / "test.log"
    setup_logging("DEBUG", str(log_file))
    assert log_file.parent.exists()


def test_cli_version(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--version"]):
        with pytest.raises(SystemExit) as exc:
            main()
        assert exc.value.code == 0
        captured = capsys.readouterr()
        assert "1.0.0" in captured.out


def test_cli_once_not_active(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--once"]):
        with patch("virtualbox_rpc.client.is_virtualbox_active", return_value=False):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            captured = capsys.readouterr()
            assert "VirtualBox is not currently active" in captured.out


def test_cli_once_active(capsys):
    mock_payload = {"details": "VirtualBox Manager", "state": "Configuring VMs"}
    with patch.object(sys, "argv", ["virtualbox-rpc", "--once"]):
        with patch(
            "virtualbox_rpc.client.VirtualBoxRPC.sync_once",
            return_value=mock_payload,
        ):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            captured = capsys.readouterr()
            assert "VirtualBox Manager" in captured.out


def test_cli_install_startup(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--install-startup"]):
        with patch("virtualbox_rpc.startup.register_startup", return_value=True):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            captured = capsys.readouterr()
            assert "Successfully registered" in captured.out


def test_cli_install_startup_failure(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--install-startup"]):
        with patch("virtualbox_rpc.startup.register_startup", return_value=False):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
            captured = capsys.readouterr()
            assert "Failed to register" in captured.err


def test_cli_uninstall_startup(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--uninstall-startup"]):
        with patch("virtualbox_rpc.startup.unregister_startup", return_value=True):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            captured = capsys.readouterr()
            assert "Successfully removed" in captured.out


def test_cli_uninstall_startup_failure(capsys):
    with patch.object(sys, "argv", ["virtualbox-rpc", "--uninstall-startup"]):
        with patch("virtualbox_rpc.startup.unregister_startup", return_value=False):
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 1
            captured = capsys.readouterr()
            assert "Failed to remove" in captured.err


def test_cli_no_tray_execution():
    with patch.object(sys, "argv", ["virtualbox-rpc", "--no-tray"]):
        with patch("virtualbox_rpc.client.VirtualBoxRPC.run") as mock_run:
            main()
            mock_run.assert_called_once()
