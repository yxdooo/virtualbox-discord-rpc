# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-10-04

### Added
- Modular package architecture under `virtualbox_rpc` with clean separation of concerns.
- Robust guest OS detection supporting Windows, Linux distributions (Ubuntu, Debian, Fedora, Arch, Kali, RedHat, openSUSE, Alpine, CentOS), macOS, and BSD.
- High-resolution remote asset icons for all supported operating systems.
- Live hardware telemetry showing allocated vCPUs and RAM.
- Multi-VM aggregation with summary details when running multiple guests simultaneously.
- Paused VM state detection and badge updates.
- Privacy configuration options (`hide_vm_name`, `hide_hardware_specs`) to prevent disclosure of sensitive host or lab information.
- VM configuration overrides (`vm_overrides`) to customize display names and icons per VM.
- Native Windows startup autostart integration via `winreg` with `--install-startup` and `--uninstall-startup` CLI arguments.
- Optional system tray controller with status indicator, pause/resume toggle, autostart management, log viewer, and graceful exit.
- Standalone PyInstaller compilation pipeline producing a single self-contained Windows executable (`VirtualBoxRPC.exe`).
- Automated multi-platform GitHub Actions CI matrix testing Python 3.9 through 3.12 across Windows, Linux, and macOS.
- Automated GitHub Actions release pipeline with SHA-256 checksum generation.
- Full unit test suite with coverage reporting.
