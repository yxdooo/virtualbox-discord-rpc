# Windows Package Manager (Winget) Submission

This directory contains the ready-to-submit manifests for publishing `virtualbox-discord-rpc` to the official Microsoft Windows Package Manager repository ([microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs)).

Once approved by Microsoft's automated validation bot, any Windows user can install the application with:

```cmd
winget install yxdooo.VirtualBoxRPC
```

---

## Submission Options

### Option 1: Automated via `wingetcreate` (Recommended)

1. Install `wingetcreate` if not already installed:
   ```cmd
   winget install Microsoft.WingetCreate
   ```
2. Submit the release binary:
   ```cmd
   wingetcreate submit https://github.com/yxdooo/virtualbox-discord-rpc/releases/download/v1.0.0/VirtualBoxRPC.exe
   ```
3. Authenticate with your GitHub account when prompted. `wingetcreate` will automatically fork `microsoft/winget-pkgs`, commit the manifests, and open a Pull Request.

---

### Option 2: Manual Pull Request to `microsoft/winget-pkgs`

1. Fork [microsoft/winget-pkgs](https://github.com/microsoft/winget-pkgs).
2. Copy the folder `winget/manifests/y/yxdooo/VirtualBoxRPC/1.0.0/` into the corresponding path in your fork:
   `manifests/y/yxdooo/VirtualBoxRPC/1.0.0/`
3. Commit with the message:
   `New package: yxdooo.VirtualBoxRPC version 1.0.0`
4. Open a Pull Request against `microsoft/winget-pkgs:master`.
5. The automated validation bot (`azure-pipelines`) will verify the hash and manifest schema within 15–30 minutes, after which it will be merged.
