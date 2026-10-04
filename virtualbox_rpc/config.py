from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger("virtualbox_rpc")

DEFAULT_CLIENT_ID = "1553096417307000954"
DEFAULT_POLLING_INTERVAL = 3
DEFAULT_LARGE_IMAGE_URL = (
    "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/virtualbox.png"
)

OS_ICONS = {
    "kali": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/kali-linux.png",
    "ubuntu": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/ubuntu-linux.png",
    "debian": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/debian-linux.png",
    "arch": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/arch-linux.png",
    "fedora": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/fedora.png",
    "windows": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/microsoft-windows.png",
    "centos": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/redhat-linux.png",
    "redhat": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/redhat-linux.png",
    "macos": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/apple.png",
    "mac": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/apple.png",
    "android": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/android.png",
    "freebsd": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/linux.png",
    "linux": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/linux.png",
    "alpine": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/alpine-linux.png",
    "mint": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/linux-mint.png",
    "manjaro": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/manjaro-linux.png",
}


@dataclass
class PrivacyConfig:
    hide_vm_name: bool = False
    hide_hardware_specs: bool = False


@dataclass
class VmOverride:
    display_name: str | None = None
    icon: str | None = None


@dataclass
class Config:
    client_id: str = DEFAULT_CLIENT_ID
    polling_interval: int = DEFAULT_POLLING_INTERVAL
    vboxmanage_path: str | None = None
    show_hardware_specs: bool = True
    log_file: str | None = "vbox_rpc.log"
    log_level: str = "INFO"
    privacy: PrivacyConfig = field(default_factory=PrivacyConfig)
    vm_overrides: dict[str, VmOverride] = field(default_factory=dict)

    @classmethod
    def load(cls, config_path: Path | None = None) -> Config:
        config = cls()

        target_path = config_path or Path("config.json")
        if target_path.exists():
            try:
                with open(target_path, encoding="utf-8") as f:
                    data = json.load(f)
                    config.client_id = data.get("client_id", config.client_id)
                    config.polling_interval = data.get("polling_interval", config.polling_interval)
                    config.vboxmanage_path = data.get("vboxmanage_path", config.vboxmanage_path)
                    config.show_hardware_specs = data.get(
                        "show_hardware_specs", config.show_hardware_specs
                    )
                    config.log_file = data.get("log_file", config.log_file)
                    config.log_level = data.get("log_level", config.log_level)

                    privacy_data = data.get("privacy", {})
                    if isinstance(privacy_data, dict):
                        config.privacy = PrivacyConfig(
                            hide_vm_name=bool(privacy_data.get("hide_vm_name", False)),
                            hide_hardware_specs=bool(
                                privacy_data.get("hide_hardware_specs", False)
                            ),
                        )

                    overrides_data = data.get("vm_overrides", {})
                    if isinstance(overrides_data, dict):
                        overrides = {}
                        for vm_key, val in overrides_data.items():
                            if isinstance(val, dict):
                                overrides[vm_key] = VmOverride(
                                    display_name=val.get("display_name"),
                                    icon=val.get("icon"),
                                )
                        config.vm_overrides = overrides

            except Exception as exc:
                logger.warning("Failed to load configuration file '%s': %s", target_path, exc)

        env_client_id = os.environ.get("VBOX_RPC_CLIENT_ID")
        if env_client_id:
            config.client_id = env_client_id

        return config
