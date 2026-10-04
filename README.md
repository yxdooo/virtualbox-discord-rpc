# VirtualBox Discord Rich Presence

A high-performance Discord Rich Presence client for Oracle VM VirtualBox. It continuously tracks virtual machine lifecycles and reflects guest operating systems, resource allocation, and execution state directly in Discord.

[![CI](https://github.com/yxdooo/virtualbox-discord-rpc/actions/workflows/ci.yml/badge.svg)](https://github.com/yxdooo/virtualbox-discord-rpc/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## Overview

Unlike naive implementations that trigger continuous COM daemon locks, `virtualbox-discord-rpc` utilizes a decoupled, non-intrusive architecture:

```text
+-----------------------+      Active?      +----------------------+
|  Process Supervisor   | ----------------> |  VBoxManage Parser   |
| (UI / Headless hosts) |      (No COM lock)|  (Cached telemetry)  |
+-----------------------+                   +----------------------+
                                                        |
                                                        v
+-----------------------+    Local IPC      +----------------------+
|     Discord Client    | <---------------- |   Presence Builder   |
| (Rich Presence Card)  |                   | (Overrides & Privacy)|
+-----------------------+                   +----------------------+
```

1. **Lightweight Process Supervisor**: Validates VirtualBox front-end and guest processes (`VirtualBox.exe`, `VirtualBoxVM.exe`, `VBoxHeadless.exe`) before querying telemetry, avoiding COM process wake-ups.
2. **Metadata Extraction**: Inspects guest configurations via `VBoxManage` to determine guest OS distribution, vCPU cores, and allocated memory.
3. **Presence Engine**: Matches OS distributions to high-resolution assets, applies user-defined privacy filters or overrides, and synchronizes with Discord via local IPC socket.

---

## Features

- **Automatic Lifecycle Tracking**: Detects when VirtualBox or individual virtual machines start and stops broadcasting as soon as VMs or the manager are closed.
- **Guest OS Identification**: Identifies common operating systems (Debian, Ubuntu, Arch Linux, Fedora, Kali, RedHat, openSUSE, Alpine, CentOS, Windows, macOS, FreeBSD, Android) and renders tailored badges.
- **Hardware Telemetry**: Displays allocated virtual CPU cores and RAM size in real time.
- **Multi-VM Aggregation**: Summarizes activity when running multiple guests simultaneously.
- **Paused State Detection**: Reflects paused VM states accurately in the presence card.
- **Privacy Controls**: Redact VM names (`hide_vm_name`) and hardware specifications (`hide_hardware_specs`) for privacy in public Discord servers.
- **VM Overrides**: Assign custom display aliases and icons to specific machines via configuration.
- **Native Autostart**: Zero-dependency Windows startup registration using the user registry (`--install-startup` / `--uninstall-startup`).
- **System Tray Controller**: Optional Windows system tray icon with live status, autostart toggle, pause/resume control, and log viewer.
- **Minimal Resource Footprint**: Consumes under 25 MB of memory and approximately 0% CPU during idle polling.

---

## Requirements

- Oracle VM VirtualBox 6.0 or newer (tested with 6.1, 7.0, and 7.1)
- Discord Desktop Client
- Python 3.9+ (source build only; not required when using standalone binary)

---

## Installation

### Method 1: Standalone Windows Binary (Recommended)

1. Download `VirtualBoxRPC.exe` and its checksum from the latest [GitHub Releases](https://github.com/yxdooo/virtualbox-discord-rpc/releases).
2. Run `VirtualBoxRPC.exe`. The application launches directly with system tray integration.
3. To start automatically on Windows login, right-click the system tray icon and check **Start with Windows**, or run:
   ```cmd
   VirtualBoxRPC.exe --install-startup
   ```

### Method 2: From Source / PyPI Package

Clone the repository and install dependencies:

```bash
git clone https://github.com/yxdooo/virtualbox-discord-rpc.git
cd virtualbox-discord-rpc

python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux / macOS:
source .venv/bin/activate

pip install --upgrade pip
pip install -e ".[tray]"
```

Run directly:

```bash
virtualbox-rpc
```

---

## Command-Line Usage

```text
usage: virtualbox-rpc [-h] [-c CONFIG] [--debug] [--once] [--install-startup]
                      [--uninstall-startup] [--no-tray] [-v]

Discord Rich Presence client for Oracle VM VirtualBox.

options:
  -h, --help           show this help message and exit
  -c, --config CONFIG  Path to custom JSON configuration file.
  --debug              Enable debug logging output.
  --once               Run a single sync check and exit.
  --install-startup    Register application to run on Windows startup.
  --uninstall-startup  Remove application from Windows startup.
  --no-tray            Disable system tray icon and run as a pure CLI process.
  -v, --version        show program's version number and exit
```

---

## Configuration

Place a `config.json` file in the working directory or specify one with `--config <path>`:

```json
{
  "client_id": "1553096417307000954",
  "polling_interval": 3,
  "vboxmanage_path": null,
  "show_hardware_specs": true,
  "log_file": "vbox_rpc.log",
  "log_level": "INFO",
  "privacy": {
    "hide_vm_name": false,
    "hide_hardware_specs": false
  },
  "vm_overrides": {
    "Lab-Production-01": {
      "display_name": "Production Workstation",
      "icon": "debian"
    }
  }
}
```

### Configuration Reference

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `client_id` | string | Built-in | Custom Discord Application Client ID. |
| `polling_interval` | integer | `3` | Frequency (seconds) for evaluating VirtualBox state. |
| `vboxmanage_path` | string / null | `null` | Explicit path to `VBoxManage` executable if not in standard PATH. |
| `show_hardware_specs` | boolean | `true` | Display allocated vCPUs and RAM specs in status line. |
| `log_file` | string / null | `"vbox_rpc.log"` | Path to write runtime logs. Set to `null` to disable file logging. |
| `log_level` | string | `"INFO"` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `privacy.hide_vm_name` | boolean | `false` | Mask machine name with generic "Virtual Machine" label. |
| `privacy.hide_hardware_specs`| boolean | `false` | Redact hardware specs while retaining OS distribution label. |
| `vm_overrides` | object | `{}` | Map of VM name to custom `display_name` and `icon`. |

---

## Development & Testing

### Running Tests and Linting

```bash
# Install development dependencies
pip install -e ".[dev]"

# Code style and formatting checks
ruff check .
ruff format --check .

# Run test suite with coverage
pytest --cov=virtualbox_rpc --cov-report=term-missing
```

### Compiling Standalone Binary

To create a single portable Windows executable with PyInstaller:

```bash
python build.py
```

The compiled binary will be placed at `dist/VirtualBoxRPC.exe`.

---

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on code style, commit conventions, and the pull request submission process.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
