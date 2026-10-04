# VirtualBox Discord Rich Presence

A lightweight, automated Discord Rich Presence client for Oracle VM VirtualBox. It monitors active virtual machines and displays real-time execution state, guest operating systems, allocated hardware specifications, and elapsed uptime on Discord.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python: 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey.svg)]()

---

## Features

- **Automated Lifecycle Sync**: Activates when VirtualBox or any VM starts, and clears Discord activity immediately upon closure without locking background daemon services.
- **Hardware & OS Detection**: Queries VBoxManage for active machine metadata, including OS distribution, CPU allocations, and memory capacity.
- **Dynamic OS Badges**: Maps the running guest OS to high-resolution badges (Debian, Kali Linux, Ubuntu, Arch, Fedora, Windows, macOS, Android, FreeBSD, and generic Linux).
- **Manager Fallback**: Displays manager navigation state when VirtualBox is open but no machines are running.
- **Low Footprint**: Consumes minimal memory (~25 MB) and 0% CPU during idle sleep cycles.

---

## Requirements

- Oracle VM VirtualBox 6.0 or newer
- Discord Desktop Client
- Python 3.8+ (not required if using standalone binary release)

---

## Installation

### Option 1: Standalone Binary (Windows)

1. Download `VirtualBoxRPC.exe` from the latest [Releases](https://github.com/yxdooo/virtualbox-discord-rpc/releases).
2. Run the executable. It operates silently in the background.

To run automatically at Windows startup, place a shortcut to the executable inside your Startup folder (`shell:startup`).

### Option 2: From Source

Clone the repository and install dependencies:

```bash
git clone https://github.com/yxdooo/virtualbox-discord-rpc.git
cd virtualbox-discord-rpc
pip install -r requirements.txt
```

Run directly:

```bash
python -m virtualbox_rpc
```

Or install in editable mode:

```bash
pip install -e .
virtualbox-rpc
```

---

## Command-Line Usage

```text
usage: virtualbox-rpc [-h] [-c CONFIG] [--debug] [--once] [-v]

Discord Rich Presence client for Oracle VM VirtualBox.

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        Path to custom JSON configuration file.
  --debug               Enable debug logging output.
  --once                Run a single sync check and exit.
  -v, --version         show program's version number and exit
```

---

## Configuration

Custom configuration can be provided via a `config.json` file in the working directory or passed via `--config`:

```json
{
  "client_id": "1553096417307000954",
  "polling_interval": 3,
  "vboxmanage_path": null,
  "show_hardware_specs": true,
  "log_file": "vbox_rpc.log",
  "log_level": "INFO"
}
```

### Configuration Options

| Option | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `client_id` | string | Built-in ID | Custom Discord Application Client ID. |
| `polling_interval` | integer | `3` | Seconds between state evaluation loops. |
| `vboxmanage_path` | string / null | `null` | Absolute path to `VBoxManage` executable if installed in non-standard location. |
| `show_hardware_specs` | boolean | `true` | Toggle display of vCPUs and RAM specs in status state. |
| `log_file` | string / null | `"vbox_rpc.log"` | Output path for runtime logs. Set to `null` to disable file logging. |
| `log_level` | string | `"INFO"` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |

---

## Building from Source

To compile a single portable executable using PyInstaller:

```bash
pip install pyinstaller
python build.py
```

The resulting binary will be placed in the `dist/` directory.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
