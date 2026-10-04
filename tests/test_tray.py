from __future__ import annotations

import sys
from unittest.mock import MagicMock, patch

from virtualbox_rpc.client import VirtualBoxRPC
from virtualbox_rpc.config import Config
from virtualbox_rpc.tray import (
    create_tray_icon,
    create_tray_image,
    is_tray_supported,
    open_log_file,
)


def test_create_tray_image():
    img = create_tray_image()
    assert img.size == (64, 64)
    assert img.mode == "RGBA"


def test_is_tray_supported():
    supported = is_tray_supported()
    assert isinstance(supported, bool)


def test_is_tray_supported_linux_no_display(monkeypatch):
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    assert is_tray_supported() is False


def test_is_tray_supported_missing_dependency():
    with patch.dict(sys.modules, {"pystray": None}):
        assert is_tray_supported() is False


def test_create_tray_icon_and_callbacks(monkeypatch):
    cfg = Config()
    service = VirtualBoxRPC(cfg)
    service.status_text = "Running 1 VM"

    if not is_tray_supported():

        class MockIcon:
            def __init__(self, name, icon, title=None, menu=None):
                self.name = name
                self.icon = icon
                self.title = title
                self.menu = menu

            def stop(self):
                pass

        monkeypatch.setattr("pystray.Icon", MockIcon)

    icon = create_tray_icon(service)
    assert icon is not None
    assert icon.title == "VirtualBox Discord RPC"

    # Verify menu structure and callbacks
    menu_items = list(icon.menu)
    assert len(menu_items) >= 5

    # First item is status text
    status_item = menu_items[0]
    assert "Running 1 VM" in str(status_item.text)

    # Pause toggle item
    pause_item = menu_items[2]
    assert "Pause" in str(pause_item.text)
    pause_item(icon)
    assert service.paused is True
    assert "Resume" in str(pause_item.text)

    # Exit item
    exit_item = menu_items[-1]
    with patch.object(service, "stop") as mock_stop, patch.object(icon, "stop") as mock_icon_stop:
        exit_item(icon)
        mock_stop.assert_called_once()
        mock_icon_stop.assert_called_once()


def test_run_with_tray_headless_fallback(monkeypatch):
    monkeypatch.setattr("virtualbox_rpc.tray.is_tray_supported", lambda: False)
    cfg = Config()
    service = VirtualBoxRPC(cfg)
    with patch.object(service, "run") as mock_run:
        from virtualbox_rpc.tray import run_with_tray

        run_with_tray(service)
        mock_run.assert_called_once()


def test_open_log_file_nonexistent(tmp_path):
    # Should not crash on nonexistent file or None
    open_log_file(None)
    open_log_file(str(tmp_path / "does_not_exist.log"))


def test_open_log_file_exists(tmp_path, monkeypatch):
    log_file = tmp_path / "test.log"
    log_file.write_text("sample log", encoding="utf-8")

    if sys.platform == "win32":
        mock_startfile = MagicMock()
        monkeypatch.setattr("os.startfile", mock_startfile, raising=False)
        open_log_file(str(log_file))
        mock_startfile.assert_called_once_with(str(log_file.resolve()))
    else:
        with patch("subprocess.run") as mock_run:
            open_log_file(str(log_file))
            mock_run.assert_called_once()
