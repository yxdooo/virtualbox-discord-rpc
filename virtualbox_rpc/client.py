import logging
import signal
import sys
import time
from typing import Optional

from pypresence import Presence

from .config import DEFAULT_LARGE_IMAGE_URL, OS_ICONS, Config
from .vbox import (
    get_running_vms,
    get_vm_specs,
    is_virtualbox_active,
    match_os_icon,
    resolve_vboxmanage_path,
)

logger = logging.getLogger("virtualbox_rpc")


def build_presence_payload(
    running_vms: list[str],
    vm_specs_map: dict[str, dict[str, str]],
    manager_start_time: Optional[int],
    vm_start_times: dict[str, int],
    config: Config,
) -> Optional[dict]:
    """Generates the Rich Presence dictionary for the given VirtualBox state."""
    if not running_vms:
        return {
            "details": "VirtualBox Manager",
            "state": "Configuring Virtual Machines",
            "start": manager_start_time or int(time.time()),
            "large_image": DEFAULT_LARGE_IMAGE_URL,
            "large_text": "Oracle VM VirtualBox",
            "buttons": [{"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}],
        }

    if len(running_vms) == 1:
        vm_name = running_vms[0]
        vm_start = vm_start_times.get(vm_name, int(time.time()))
        details_text = f"Running: {vm_name}"[:128]

        vm_info = vm_specs_map.get(
            vm_name, {"ostype": "Virtual Machine", "specs": "", "state": "running"}
        )
        ostype = vm_info.get("ostype", "Virtual Machine")
        specs = vm_info.get("specs", "")
        state = vm_info.get("state", "running")

        if state == "paused":
            state_text = f"Paused ({ostype})"[:128]
        elif config.show_hardware_specs and specs:
            state_text = f"{ostype} ({specs})"[:128]
        else:
            state_text = ostype[:128]

        icon_url = match_os_icon(vm_name, ostype)

        return {
            "details": details_text,
            "state": state_text,
            "start": vm_start,
            "large_image": DEFAULT_LARGE_IMAGE_URL,
            "large_text": "Oracle VM VirtualBox",
            "small_image": icon_url,
            "small_text": ostype[:128],
            "buttons": [{"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}],
        }

    # Multiple active VMs
    details_text = f"Running {len(running_vms)} Virtual Machines"[:128]
    state_text = f"VMs: {', '.join(running_vms)}"[:128]
    start_time = min(vm_start_times.values()) if vm_start_times else int(time.time())

    return {
        "details": details_text,
        "state": state_text,
        "start": start_time,
        "large_image": DEFAULT_LARGE_IMAGE_URL,
        "large_text": "Oracle VM VirtualBox",
        "small_image": OS_ICONS["linux"],
        "small_text": "Multiple VMs Active",
        "buttons": [{"label": "VirtualBox Website", "url": "https://www.virtualbox.org/"}],
    }


class VirtualBoxRPC:
    """Manages the lifecycle of the Discord Rich Presence client for VirtualBox."""

    def __init__(self, config: Config):
        self.config = config
        self.vboxmanage = resolve_vboxmanage_path(config.vboxmanage_path)
        self.rpc: Optional[Presence] = None
        self.connected = False
        self.running = False

        self.manager_start_time: Optional[int] = None
        self.vm_start_times: dict[str, int] = {}
        self.last_state_hash: Optional[tuple[str, str]] = None

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

    def sync_once(self) -> Optional[dict]:
        """Calculates current state payload once without persisting a connection loop."""
        if not is_virtualbox_active():
            return None

        running_vms = get_running_vms(self.vboxmanage)
        vm_specs_map = {}
        for name in running_vms:
            vm_specs_map[name] = get_vm_specs(self.vboxmanage, name)

        now = int(time.time())
        vm_starts = {name: now for name in running_vms}
        return build_presence_payload(running_vms, vm_specs_map, now, vm_starts, self.config)

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

        # Cleanup stopped VMs
        for name in list(self.vm_start_times.keys()):
            if name not in running_vms:
                del self.vm_start_times[name]

        now = int(time.time())
        for name in running_vms:
            if name not in self.vm_start_times:
                self.vm_start_times[name] = now

        vm_specs_map = {}
        for name in running_vms:
            vm_specs_map[name] = get_vm_specs(self.vboxmanage, name)

        payload = build_presence_payload(
            running_vms=running_vms,
            vm_specs_map=vm_specs_map,
            manager_start_time=self.manager_start_time,
            vm_start_times=self.vm_start_times,
            config=self.config,
        )

        if not payload:
            return

        current_hash = (payload.get("details", ""), payload.get("state", ""))
        if current_hash != self.last_state_hash:
            self.rpc.update(**payload)
            self.last_state_hash = current_hash
            logger.info("Presence updated: %s | %s", current_hash[0], current_hash[1])

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
