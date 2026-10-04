import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional
import psutil

from .config import OS_ICONS


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


def get_running_vms(vboxmanage_path: Optional[Path]) -> List[str]:
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
        vms = []
        for line in proc.stdout.strip().splitlines():
            line = line.strip()
            if line.startswith('"'):
                name = line.split('"')[1]
                vms.append(name)
        return vms
    except Exception:
        return []


def get_vm_specs(vboxmanage_path: Optional[Path], vm_name: str) -> Dict[str, str]:
    """Extracts OS type, CPU cores, and memory capacity for a given VM."""
    info = {"ostype": "Virtual Machine", "specs": ""}
    if not vboxmanage_path or not vboxmanage_path.is_file():
        return info

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

        ostype = "Virtual Machine"
        cpus = ""
        memory = ""

        for line in proc.stdout.strip().splitlines():
            if line.startswith("ostype="):
                ostype = line.split("=", 1)[1].strip('"')
            elif line.startswith("memory="):
                mb = int(line.split("=", 1)[1].strip('"'))
                memory = f"{round(mb / 1024, 1)} GB RAM" if mb >= 1024 else f"{mb} MB RAM"
            elif line.startswith("cpus="):
                cpu_count = line.split("=", 1)[1].strip('"')
                cpus = f"{cpu_count} vCPU{'s' if int(cpu_count) > 1 else ''}"

        parts = [p for p in (cpus, memory) if p]
        info["ostype"] = ostype
        info["specs"] = " • ".join(parts)
    except Exception:
        pass

    return info


def match_os_icon(vm_name: str, ostype: str) -> str:
    """Selects an icon badge URL matching the operating system family."""
    search = f"{vm_name.lower()} {ostype.lower()}"
    for key, url in OS_ICONS.items():
        if key in search:
            return url
    return OS_ICONS["linux"]
