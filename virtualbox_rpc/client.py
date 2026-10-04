import logging
import signal
import sys
import time
from typing import Dict, Optional, Tuple
from pypresence import Presence

from .config import Config, DEFAULT_LARGE_IMAGE_URL, OS_ICONS
from .vbox import (
    get_running_vms,
    get_vm_specs,
    is_virtualbox_active,
    match_os_icon,
    resolve_vboxmanage_path,
)

logger = logging.getLogger("virtualbox_rpc")


class VirtualBoxRPC:
    """Manages the lifecycle of the Discord Rich Presence client for VirtualBox."""

    def __init__(self, config: Config):
        self.config = config
        self.vboxmanage = resolve_vboxmanage_path(config.vboxmanage_path)
        self.rpc: Optional[Presence] = None
        self.connected = False
        self.running = False

        self.manager_start_time: Optional[int] = None
        self.vm_start_times: Dict[str, int] = {}
        self.last_state_hash: Optional[Tuple[str, str]] = None

    def connect(self) -> bool:
        """Establishes an IPC connection with the local Discord client."""
        if self.connected and self.rpc:
            return True

        try:
            self.rpc = Presence(self.config.client_id)
            self.rpc.connect()
            self.connected = True
            logger.info("Connected to Discord IPC socket.")
            return True
        except Exception as exc:
            logger.debug("Discord socket connection failed: %s", exc)
            self.rpc = None
            self.connected = False
            return False

    def disconnect(self) -> None:
        """Clears the active presence and closes the IPC socket."""
        if self.rpc:
            try:
                self.rpc.clear()
            except Exception:
                pass
            try:
                self.rpc.close()
            except Exception:
                pass

        self.rpc = None
        self.connected = False
        self.manager_start_time = None
        self.vm_start_times.clear()
        self.last_state_hash = None
        logger.info("Cleared Discord presence and closed connection.")

    def _sync_presence(self) -> None:
        """Evaluates VirtualBox state and updates the Discord presence payload."""
        if not is_virtualbox_active():
            if self.connected:
                self.disconnect()
            return

        if not self.connected:
            if not self.connect():
                return
            self.manager_start_time = int(time.time())

        running_vms = get_running_vms(self.vboxmanage)

        if running_vms:
            # Drop start times for stopped VMs
            for name in list(self.vm_start_times.keys()):
                if name not in running_vms:
                    del self.vm_start_times[name]

            # Record start times for newly started VMs
            for name in running_vms:
                if name not in self.vm_start_times:
                    self.vm_start_times[name] = int(time.time())

            if len(running_vms) == 1:
                vm_name = running_vms[0]
                vm_start = self.vm_start_times.get(vm_name, int(time.time()))
                details_text = f"Running: {vm_name}"[:128]

                vm_info = get_vm_specs(self.vboxmanage, vm_name)
                ostype = vm_info["ostype"]
                specs = vm_info["specs"]

                if self.config.show_hardware_specs and specs:
                    state_text = f"{ostype} ({specs})"[:128]
                else:
                    state_text = ostype[:128]

                icon_url = match_os_icon(vm_name, ostype)
                current_hash = (details_text, state_text)

                if current_hash != self.last_state_hash:
                    self.rpc.update(
                        details=details_text,
                        state=state_text,
                        start=vm_start,
                        large_image=DEFAULT_LARGE_IMAGE_URL,
                        large_text="Oracle VM VirtualBox",
                        small_image=icon_url,
                        small_text=ostype[:128],
                        buttons=[
                            {"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}
                        ],
                    )
                    self.last_state_hash = current_hash
                    logger.info("Presence updated: %s | %s", details_text, state_text)

            else:
                details_text = f"Running {len(running_vms)} Virtual Machines"[:128]
                state_text = f"VMs: {', '.join(running_vms)}"[:128]
                start_time = min(self.vm_start_times.values()) if self.vm_start_times else int(time.time())
                current_hash = (details_text, state_text)

                if current_hash != self.last_state_hash:
                    self.rpc.update(
                        details=details_text,
                        state=state_text,
                        start=start_time,
                        large_image=DEFAULT_LARGE_IMAGE_URL,
                        large_text="Oracle VM VirtualBox",
                        small_image=OS_ICONS["linux"],
                        small_text="Multiple VMs Active",
                        buttons=[
                            {"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}
                        ],
                    )
                    self.last_state_hash = current_hash
                    logger.info("Presence updated: %s | %s", details_text, state_text)

        else:
            # Manager window open with no running VMs
            if self.manager_start_time is None:
                self.manager_start_time = int(time.time())

            details_text = "VirtualBox Manager"
            state_text = "Configuring Virtual Machines"
            current_hash = (details_text, state_text)

            if current_hash != self.last_state_hash:
                self.rpc.update(
                    details=details_text,
                    state=state_text,
                    start=self.manager_start_time,
                    large_image=DEFAULT_LARGE_IMAGE_URL,
                    large_text="Oracle VM VirtualBox",
                    buttons=[
                        {"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}
                    ],
                )
                self.last_state_hash = current_hash
                logger.info("Presence updated: %s | %s", details_text, state_text)

    def run(self) -> None:
        """Main service loop monitoring VirtualBox state."""
        self.running = True

        def _handle_exit(sig, frame):
            logger.info("Shutdown signal received (%s). Exiting.", sig)
            self.running = False
            self.disconnect()
            sys.exit(0)

        signal.signal(signal.SIGINT, _handle_exit)
        signal.signal(signal.SIGTERM, _handle_exit)

        logger.info(
            "Service started. Polling every %ds (VBoxManage: %s)",
            self.config.polling_interval,
            self.vboxmanage or "not found",
        )

        while self.running:
            try:
                self._sync_presence()
            except Exception as exc:
                logger.debug("Exception during presence sync: %s", exc)
                if self.rpc:
                    try:
                        self.rpc.close()
                    except Exception:
                        pass
                self.rpc = None
                self.connected = False
                self.last_state_hash = None

            time.sleep(self.config.polling_interval)
