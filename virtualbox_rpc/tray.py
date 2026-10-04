from __future__ import annotations

import logging
import os
import subprocess
import sys
import threading
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from .startup import is_startup_registered, register_startup, unregister_startup

if TYPE_CHECKING:
    from .client import VirtualBoxRPC

logger = logging.getLogger("virtualbox_rpc")


def is_tray_supported() -> bool:
    """Checks whether system tray dependencies and display environment are available."""
    try:
        import PIL  # noqa: F401
        import pystray  # noqa: F401
    except ImportError:
        return False

    if sys.platform.startswith("linux"):
        # Requires an active X11 or Wayland display session
        if not (os.environ.get("DISPLAY") or os.environ.get("WAYLAND_DISPLAY")):
            return False

    return True


def create_tray_image():
    """Generates a clean 64x64 RGBA icon for the system tray."""
    from PIL import Image, ImageDraw

    width, height = 64, 64
    image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # VirtualBox dark blue container
    draw.rounded_rectangle([4, 4, 60, 60], radius=12, fill=(24, 91, 157, 255))

    # 3D isometric cube facets
    # Top face
    draw.polygon(
        [(32, 14), (50, 24), (32, 34), (14, 24)],
        fill=(40, 140, 220, 255),
        outline=(255, 255, 255, 220),
    )
    # Left face
    draw.polygon(
        [(14, 24), (32, 34), (32, 52), (14, 42)],
        fill=(20, 80, 150, 255),
        outline=(255, 255, 255, 220),
    )
    # Right face
    draw.polygon(
        [(32, 34), (50, 24), (50, 42), (32, 52)],
        fill=(30, 110, 190, 255),
        outline=(255, 255, 255, 220),
    )

    return image


def open_log_file(log_path_str: str | None) -> None:
    """Opens the application log file with the system default text viewer."""
    if not log_path_str:
        return

    log_path = Path(log_path_str).resolve()
    if not log_path.exists():
        logger.warning("Log file '%s' does not exist yet.", log_path)
        return

    try:
        if sys.platform == "win32":
            os.startfile(str(log_path))
        elif sys.platform == "darwin":
            subprocess.run(["open", str(log_path)], check=False)
        else:
            subprocess.run(["xdg-open", str(log_path)], check=False)
    except Exception as exc:
        logger.error("Failed to open log file '%s': %s", log_path, exc)


def create_tray_icon(service: VirtualBoxRPC, on_exit: Callable[[], None] | None = None):
    """Builds the pystray.Icon instance with contextual menu items."""
    import pystray

    image = create_tray_image()

    def _get_status_text(item=None) -> str:
        return f"Status: {service.status_text}"

    def _get_pause_label(item=None) -> str:
        return "Resume Presence" if service.paused else "Pause Presence"

    def _on_toggle_pause(icon, item):
        service.toggle_pause()

    def _on_toggle_startup(icon, item):
        if is_startup_registered():
            unregister_startup()
        else:
            register_startup()

    def _on_open_logs(icon, item):
        open_log_file(service.config.log_file)

    def _on_quit(icon, item):
        logger.info("Tray Exit requested by user.")
        service.stop()
        icon.stop()
        if on_exit:
            on_exit()

    menu_items = [
        pystray.MenuItem(_get_status_text, action=None, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem(_get_pause_label, _on_toggle_pause),
        pystray.MenuItem(
            "Start with Windows",
            _on_toggle_startup,
            checked=lambda item: is_startup_registered(),
            visible=lambda item: sys.platform == "win32",
        ),
        pystray.MenuItem("Open Log File", _on_open_logs),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem("Exit", _on_quit),
    ]

    icon = pystray.Icon(
        "VirtualBoxRPC",
        image,
        "VirtualBox Discord RPC",
        menu=pystray.Menu(*menu_items),
    )
    return icon


def run_with_tray(service: VirtualBoxRPC) -> None:
    """Launches the service in a background worker thread and manages the system tray on the main thread."""
    worker = threading.Thread(target=service.run, daemon=True, name="RPCWorker")
    worker.start()

    icon = create_tray_icon(service)
    try:
        icon.run()
    finally:
        service.stop()
        if worker.is_alive():
            worker.join(timeout=2.0)
