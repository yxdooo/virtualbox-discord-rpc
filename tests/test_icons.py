from __future__ import annotations

from virtualbox_rpc.config import OS_ICONS
from virtualbox_rpc.vbox import match_os_icon


def test_match_os_icon_by_vm_name():
    assert match_os_icon("kali-linux-2026", "Linux") == OS_ICONS["kali"]
    assert match_os_icon("MyUbuntuBox", "Other") == OS_ICONS["ubuntu"]
    assert match_os_icon("arch-dev", "Linux") == OS_ICONS["arch"]
    assert match_os_icon("Win11-VM", "Windows") == OS_ICONS["windows"]


def test_match_os_icon_by_ostype():
    assert match_os_icon("vm1", "Debian (64-bit)") == OS_ICONS["debian"]
    assert match_os_icon("my-server", "Fedora (64-bit)") == OS_ICONS["fedora"]
    assert match_os_icon("apple-vm", "Mac OS X (64-bit)") == OS_ICONS["macos"]


def test_match_os_icon_fallback():
    assert match_os_icon("unknown-vm", "Unknown OS") == OS_ICONS["linux"]
