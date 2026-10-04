#!/usr/bin/env python3
"""Build script for compiling VirtualBox Discord RPC into a standalone executable."""

import importlib.util
import subprocess
import sys
from pathlib import Path


def build():
    if importlib.util.find_spec("PyInstaller") is None:
        print("PyInstaller is not installed. Run: pip install pyinstaller")
        sys.exit(1)

    root_dir = Path(__file__).parent.resolve()
    entrypoint = root_dir / "virtualbox_rpc" / "__main__.py"

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        "--clean",
        "--onefile",
        "--windowed",
        "--name",
        "VirtualBoxRPC",
        "--hidden-import=pystray",
        "--hidden-import=PIL",
        str(entrypoint),
    ]

    print("Building standalone executable...")
    result = subprocess.run(cmd, cwd=root_dir)

    if result.returncode == 0:
        exe_path = (
            root_dir
            / "dist"
            / ("VirtualBoxRPC.exe" if sys.platform == "win32" else "VirtualBoxRPC")
        )
        print(f"Build successful. Output: {exe_path}")
    else:
        print("Build failed.")
        sys.exit(result.returncode)


if __name__ == "__main__":
    build()
