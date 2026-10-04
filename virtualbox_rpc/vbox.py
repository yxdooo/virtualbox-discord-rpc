import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import psutil

from .config import OS_ICONS


@dataclass
class VmInfo:
    """Holds metadata for an active virtual machine."""

    name: str = ""
    ostype: str = "Virtual Machine"
    specs: str = ""
    state: str = "running"
    memory_mb: int = 0
    cpus: int = 0


def resolve_vboxmanage_path(custom_path: Optional[str] = None) -> Optional[Path]:
    """Locates the VBoxManage binary across Windows, Linux, and macOS."""
    if custom_path:
        path = Path(custom_path)
        if path.is_file():
            return path

    binary_name = "VBoxManage.exe" if sys.platform == "win32" else "vboxmanage"
    system_path = shutil.which(binary_name) or shutil.which("VBoxManage")
    if system_path:
        return Path(system_path)

    if sys.platform == "win32":
        candidates = [
            os.environ.get("VBOX_MSI_INSTALL_PATH", ""),
            os.environ.get("VBOX_INSTALL_PATH", ""),
            r"C:\Program Files\Oracle\VirtualBox",
            r"C:\Program Files (x86)\Oracle\VirtualBox",
        ]
        for candidate in candidates:
            if candidate:
                exe = Path(candidate) / "VBoxManage.exe"
                if exe.is_file():
                    return exe

    elif sys.platform == "darwin":
        mac_path = Path("/Applications/VirtualBox.app/Contents/MacOS/VBoxManage")
        if mac_path.is_file():
            return mac_path

    elif sys.platform.startswith("linux"):
        for linux_path in [Path("/usr/bin/vboxmanage"), Path("/usr/local/bin/vboxmanage")]:
            if linux_path.is_file():
                return linux_path

    return None


def is_virtualbox_active() -> bool:
    """
    Checks if VirtualBox Manager or any active VM window is running.
    VBoxSVC is deliberately omitted because it is a background COM service
    and remains active after windows are closed, which would prevent status clearing.
    """
    targets = {
        "virtualbox.exe",
        "virtualboxvm.exe",
        "vboxheadless.exe",
        "virtualbox",
        "virtualboxvm",
        "vboxheadless",
    }
    for proc in psutil.process_iter(["name"]):
        try:
            name = proc.info.get("name")
            if name and name.lower() in targets:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return False


def parse_running_vms(raw_output: str) -> list[str]:
    """Parses standard VBoxManage list runningvms text into a list of VM names."""
    vms: list[str] = []
    for line in raw_output.strip().splitlines():
        line = line.strip()
        if line.startswith('"'):
            end_quote = line.find('"', 1)
            if end_quote != -1:
                vms.append(line[1:end_quote])
    return vms


def get_running_vms(vboxmanage_path: Optional[Path]) -> list[str]:
    """Queries VBoxManage for active virtual machine names."""
    if not vboxmanage_path or not vboxmanage_path.is_file():
        return []

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        proc = subprocess.run(
            [str(vboxmanage_path), "list", "runningvms"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
            startupinfo=startupinfo,
            encoding="utf-8",
            errors="ignore",
        )
        return parse_running_vms(proc.stdout)
    except Exception:
        return []


def parse_vminfo(raw_output: str, vm_name: str = "") -> VmInfo:
    """Parses machine-readable VBoxManage showvminfo key-value output."""
    info = VmInfo(name=vm_name)
    cpus_str = ""
    memory_str = ""

    for line in raw_output.strip().splitlines():
        line = line.strip()
        if not line or "=" not in line:
            continue

        key, _, val = line.partition("=")
        val = val.strip('"')

        if key == "name" and not vm_name:
            info.name = val
        elif key == "ostype":
            info.ostype = val
        elif key == "VMState":
            info.state = val.lower()
        elif key == "memory":
            try:
                mb = int(val)
                info.memory_mb = mb
                memory_str = f"{round(mb / 1024, 1)} GB RAM" if mb >= 1024 else f"{mb} MB RAM"
            except ValueError:
                pass
        elif key == "cpus":
            try:
                count = int(val)
                info.cpus = count
                cpus_str = f"{count} vCPU{'s' if count > 1 else ''}"
            except ValueError:
                pass

    parts = [p for p in (cpus_str, memory_str) if p]
    info.specs = " • ".join(parts)
    return info


def get_vm_specs(vboxmanage_path: Optional[Path], vm_name: str) -> dict[str, str]:
    """Retrieves formatted VM specs and ostype via VBoxManage."""
    if not vboxmanage_path or not vboxmanage_path.is_file():
        return {"ostype": "Virtual Machine", "specs": "", "state": "running"}

    startupinfo = None
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

    try:
        proc = subprocess.run(
            [str(vboxmanage_path), "showvminfo", vm_name, "--machinereadable"],
            capture_output=True,
            text=True,
            timeout=3,
            check=False,
            startupinfo=startupinfo,
            encoding="utf-8",
            errors="ignore",
        )
        parsed = parse_vminfo(proc.stdout, vm_name=vm_name)
        return {
            "ostype": parsed.ostype,
            "specs": parsed.specs,
            "state": parsed.state,
        }
    except Exception:
        return {"ostype": "Virtual Machine", "specs": "", "state": "running"}


def match_os_icon(vm_name: str, ostype: str) -> str:
    """Selects an icon badge URL matching the operating system family."""
    search = f"{vm_name.lower()} {ostype.lower()}"
    for key, url in OS_ICONS.items():
        if key in search:
            return url
    return OS_ICONS["linux"]
