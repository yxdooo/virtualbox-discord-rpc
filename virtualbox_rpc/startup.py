from __future__ import annotations

import logging
import sys
from pathlib import Path

logger = logging.getLogger("virtualbox_rpc")

REG_SUBKEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "VirtualBoxDiscordRPC"


def is_windows() -> bool:
    """Returns True if running on Microsoft Windows."""
    return sys.platform == "win32"


def get_startup_command() -> str:
    """Resolves the executable command used to launch the background service."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"'

    python_exe = Path(sys.executable)
    pythonw = python_exe.parent / "pythonw.exe"
    executable = pythonw if pythonw.exists() else python_exe
    return f'"{executable}" -m virtualbox_rpc'


def is_startup_registered() -> bool:
    """Checks whether the application is registered in Windows startup."""
    if not is_windows():
        return False

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_READ) as key:
            winreg.QueryValueEx(key, APP_NAME)
            return True
    except (FileNotFoundError, OSError):
        return False


def register_startup(command: str | None = None) -> bool:
    """Registers the application to launch automatically on Windows login."""
    if not is_windows():
        logger.error("Startup registration is only supported on Windows.")
        return False

    import winreg

    cmd = command or get_startup_command()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, cmd)
            logger.info("Successfully registered startup entry: %s", cmd)
            return True
    except OSError as exc:
        logger.error("Failed to register Windows startup key: %s", exc)
        return False


def unregister_startup() -> bool:
    """Removes the application from Windows startup."""
    if not is_windows():
        logger.error("Startup management is only supported on Windows.")
        return False

    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_SUBKEY, 0, winreg.KEY_SET_VALUE) as key:
            winreg.DeleteValue(key, APP_NAME)
            logger.info("Successfully removed startup entry for %s", APP_NAME)
            return True
    except FileNotFoundError:
        logger.info("Startup entry for %s was not present.", APP_NAME)
        return True
    except OSError as exc:
        logger.error("Failed to delete Windows startup key: %s", exc)
        return False
