import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

DEFAULT_CLIENT_ID = "1553096417307000954"
DEFAULT_POLLING_INTERVAL = 3
DEFAULT_LARGE_IMAGE_URL = (
    "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/virtualbox.png"
)

OS_ICONS = {
    "kali": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/kali-linux.png",
    "ubuntu": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/ubuntu.png",
    "debian": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/debian.png",
    "arch": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/arch-linux.png",
    "fedora": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/fedora.png",
    "windows": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/windows.png",
    "centos": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/centos.png",
    "redhat": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/redhat.png",
    "macos": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/apple.png",
    "mac": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/apple.png",
    "android": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/android.png",
    "freebsd": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/freebsd.png",
    "linux": "https://raw.githubusercontent.com/walkxcode/dashboard-icons/main/png/linux.png",
}


@dataclass
class Config:
    client_id: str = DEFAULT_CLIENT_ID
    polling_interval: int = DEFAULT_POLLING_INTERVAL
    vboxmanage_path: Optional[str] = None
    show_hardware_specs: bool = True
    log_file: Optional[str] = "vbox_rpc.log"
    log_level: str = "INFO"

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
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
            except Exception:
                pass

        env_client_id = os.environ.get("VBOX_RPC_CLIENT_ID")
        if env_client_id:
            config.client_id = env_client_id

        return config
